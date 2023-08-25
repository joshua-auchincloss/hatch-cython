import os
import subprocess
import sys
from contextlib import contextmanager
from glob import glob
from logging import getLogger
from tempfile import TemporaryDirectory
from typing import ClassVar, Optional, ParamSpec

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

logger = getLogger(__name__)

P = ParamSpec("P")

DIRECTIVES = {"binding": True, "language_level": 3}


def setup_py(
    *files: list[str],
    compile_args: Optional[list[str]] = None,
    directives: Optional[dict] = None,
    includes: Optional[list[str]] = None,
    include_numpy: Optional[bool] = False,
    **kwargs,
):
    if compile_args is None:
        compile_args = ["-O2"]
    if directives is None:
        directives = DIRECTIVES
    else:
        directives = {**DIRECTIVES, **{k: v for k, v in directives.items() if v is not None}}
    if includes is None:
        includes = []

    if include_numpy:
        from numpy import get_include

        includes.append(get_include())

    code = """
from setuptools import Extension, setup
from Cython.Build import cythonize

COMPILEARGS = {compile_args}
DIRECTIVES = {directives}
INCLUDES = {includes}

if __name__ == "__main__":
    exts = [
    Extension("*", [
                {ext_files}
            ],
            extra_compile_args=COMPILEARGS,
        {keywords}
        ),
    ]
    ext_modules = cythonize(
            exts,
            compiler_directives=DIRECTIVES,
            include_path=INCLUDES
    )
    setup(ext_modules=ext_modules)
"""
    ext_files = ",\n\t".join(f'"{f}"' for f in files)
    kwds = ",\n\t".join((f'{k}="{v}"' for k, v in kwargs.items()))
    return code.format(
        compile_args=repr(compile_args),
        directives=repr(directives),
        ext_files=ext_files,
        keywords=kwds,
        includes=repr(includes),
    ).strip()


class CythonBuildHook(BuildHookInterface):
    PLUGIN_NAME = "cython"

    precompiled_extension = ".pyx"
    compiled_extensions: ClassVar[list] = [
        ".c",
        ".cpp",
        # unix
        ".so",
        # windows
        ".dll",
        ".pyd",
    ]

    _included: list[str]
    _artifact_patterns: list[str]
    _artifact_globs: list[str]
    _norm_included_files: list[str]
    _norm_artifact_patterns: list[str]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._included = None
        self._norm_included_files = None
        self._artifact_patterns = None
        self._artifact_globs = None
        self._norm_artifact_patterns = None

    @property
    def is_src(self):
        return os.path.exists(os.path.join(self.root, "src"))

    @property
    def is_windows(self):
        return os.name.lower() == "nt"

    def normalize_path(self, pattern: str):
        if self.is_windows:
            return pattern.replace("/", "\\")
        return pattern.replace("\\", "/")

    def normalize_glob(self, pattern: str):
        return pattern.replace("\\", "/")

    @property
    def included_files(self):
        if self._included is None:
            if self.is_src:
                pattern = "./src/**/*.pyx"
            else:
                pattern = "./**/*.pyx"
            self._included = glob(pattern)
        return self._included

    @property
    def normalized_included_files(self):
        """
        Produces files in posix format
        """
        if self._norm_included_files is None:
            self._norm_included_files = [self.normalize_glob(f) for f in self.included_files]
        return self._norm_included_files

    @property
    def artifact_globs(self):
        if self._artifact_globs is None:
            artifact_globs = []
            for included_file in self.normalized_included_files:
                root, _ = os.path.splitext(included_file)
                artifact_globs.append(f"{root}.*{self.precompiled_extension}")
            self._artifact_globs = artifact_globs
        return self._artifact_globs

    @property
    def normalized_artifact_globs(self):
        """
        Produces files in platform native format (e.g. a/b vs a\\b)
        """
        if self._norm_artifact_patterns is None:
            self._norm_artifact_patterns = [self.normalize_glob(f) for f in self.artifact_globs]
        return self._norm_artifact_patterns

    @property
    def artifact_patterns(self):
        if self._artifact_patterns is None:
            self._artifact_patterns = [f"/{artifact_glob}" for artifact_glob in self.normalized_artifact_globs]
        return self._artifact_patterns

    @contextmanager
    def get_build_dirs(self):
        with TemporaryDirectory() as temp_dir:
            real = os.path.realpath(temp_dir)
            yield real, real

    @property
    def compiled(self):
        if self.is_src:
            root = "./src/"
        else:
            root = "./"
        globs = [f"{root}/**/*{ext}" for ext in self.compiled_extensions]
        globbed = []
        for g in globs:
            globbed += [self.normalize_path(f) for f in glob(g)]

        return list(set(globbed))

    @property
    def inclusion_map(self):
        include = {}
        for compl in self.compiled:
            include[compl] = compl
        return include

    def clean(self, _versions: list[str]):
        for f in self.compiled:
            os.remove(f)

    def initialize(self, version: str, build_data: dict):
        if self.target_name != "wheel":
            return
        compile_args = self.config.get("compile-args")
        if compile_args is not None:
            if not isinstance(compile_args, list):
                msg = "compile-args must be a list, got %s" % type(compile_args)
                raise ValueError(msg)

        binding = self.config.get("binding")
        if binding is not None:
            if not isinstance(binding, bool):
                msg = "binding must be a bool, got %s" % type(binding)
                raise ValueError(msg)

        llevel = self.config.get("language-level")
        if llevel is not None:
            if not isinstance(llevel, (int)):
                msg = "language-level must be an int, got %s" % type(llevel)
                raise ValueError(msg)

        includes = self.config.get("includes")
        if includes is not None:
            if not isinstance(includes, (list)):
                msg = "includes must be a list, got %s" % type(includes)
                raise ValueError(msg)

        numpy = self.config.get("include-numpy")
        if numpy is not None:
            if not isinstance(numpy, bool):
                msg = "include-numpy must be a bool, got %s" % type(numpy)
                raise ValueError(msg)

        self.app.display_waiting("pre-build artifacts")
        self.app.display_waiting(glob("./*/**"))

        with self.get_build_dirs() as (config, temp):
            shared_temp_build_dir = os.path.join(config, "build")
            temp_build_dir = os.path.join(temp, "tmp")
            os.mkdir(shared_temp_build_dir)
            os.mkdir(temp_build_dir)
            self.clean([version])

            setup_file = os.path.join(temp, "setup.py")
            with open(setup_file, "w") as f:
                setup = setup_py(
                    *self.normalized_included_files,
                    compile_args=compile_args,
                    directives={
                        "binding": binding,
                        "language_level": llevel,
                    },
                    includes=includes,
                    include_numpy=numpy,
                    **self.config,
                )
                f.write(setup)

            process = subprocess.run(  # noqa: PLW1510
                [  # noqa: S603
                    sys.executable,
                    setup_file,
                    "build_ext",
                    "--inplace",
                    "--build-lib",
                    shared_temp_build_dir,
                    "--build-temp",
                    temp_build_dir,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if process.returncode:
                self.app.display_error(f"cythonize exited non null status {process.returncode}")
                self.app.display_error(process.stdout.decode("utf-8"))
                msg = "failed compilation"
                raise Exception(msg)

            self.app.display_success("post build artifacts")
            self.app.display_success(glob(f"{temp}/build/**/*.*"))

        build_data["infer_tag"] = True
        build_data["pure_python"] = False
        build_data["artifacts"].extend(self.artifact_patterns)
        build_data["force_include"].update(self.inclusion_map)
