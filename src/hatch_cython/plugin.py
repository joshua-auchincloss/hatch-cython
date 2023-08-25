import os
import subprocess
import sys
from contextlib import contextmanager
from glob import glob
from tempfile import TemporaryDirectory
from typing import ClassVar, ParamSpec

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from hatch_cython.config import Config, parse_from_dict

P = ParamSpec("P")

DIRECTIVES = {"binding": True, "language_level": 3}


def setup_py(
    *files: list[str],
    options: Config,
):
    code = """
from setuptools import Extension, setup
from Cython.Build import cythonize

COMPILEARGS = {compile_args}
DIRECTIVES = {directives}
INCLUDES = {includes}
LIBRARIES = {libs}
LIBRARY_DIRS = {lib_dirs}

if __name__ == "__main__":
    exts = [
    Extension("*", [
                ex
            ],
            extra_compile_args=COMPILEARGS,
            include_dirs=INCLUDES,
            libraries=LIBRARIES,
            library_dirs=LIBRARY_DIRS,
        {keywords}
        ) for ex in ({ext_files})
    ]
    ext_modules = cythonize(
            exts,
            compiler_directives=DIRECTIVES,
            include_path=INCLUDES
    )
    setup(ext_modules=ext_modules)
"""
    ext_files = ",\n\t".join(f'"{f}"' for f in files)
    kwds = ",\n\t".join((f'{k}="{v}"' for k, v in options.compile_kwargs.items()))
    return code.format(
        compile_args=repr(options.compile_args_for_platform),
        directives=repr(options.directives),
        ext_files=ext_files,
        keywords=kwds,
        includes=repr(options.includes),
        libs=repr(options.libraries),
        lib_dirs=repr(options.library_dirs),
    ).strip()


class CythonBuildHook(BuildHookInterface):
    PLUGIN_NAME = "cython"

    precompiled_extension = ".pyx"
    intermediate_extensions: ClassVar[list] = [
        ".c",
        ".cpp",
    ]
    compiled_extensions: ClassVar[list] = [
        # unix
        ".so",
        # windows
        ".dll",
        ".pyd",
    ]

    _config: Config
    _dir: str
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
        self._config = None
        self._dir = None

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
    def project_dir(self):
        if self._dir is None:
            if self.is_src:
                src = f"./src/{self.metadata.name}"
            else:
                src = f"./{self.metadata.name}"
            self._dir = src
        return self._dir

    @property
    def precompiled_globs(self):
        return [f"{self.project_dir}/*.pyx", f"{self.project_dir}/**/*.pyx"]

    @property
    def included_files(self):
        if self._included is None:
            self._included = []
            for patt in self.precompiled_globs:
                self._included.extend(glob(patt))
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
            yield os.path.realpath(temp_dir)

    def _globs(self, exts: list[str]):
        globs = [
            *(f"{self.project_dir}/**/*{ext}" for ext in exts),
            *(f"{self.project_dir}/*{ext}" for ext in exts),
        ]
        globbed = []
        for g in globs:
            globbed += [self.normalize_path(f) for f in glob(g)]
        return list(set(globbed))

    @property
    def intermediate(self):
        return self._globs(self.intermediate_extensions)

    @property
    def compiled(self):
        return self._globs(self.compiled_extensions)

    @property
    def inclusion_map(self):
        include = {}
        for compl in self.compiled:
            include[compl] = compl
        return include

    def rm_recurse(self, li: list[str]):
        for f in li:
            os.remove(f)

    def clean_intermediate(self):
        self.rm_recurse(self.intermediate)

    def clean_compiled(self):
        self.rm_recurse(self.compiled)

    def clean(self, _versions: list[str]):
        self.clean_intermediate()
        self.clean_compiled()

    @property
    def options(self):
        if self._config is None:
            self._config = parse_from_dict(self)
        return self._config

    def initialize(self, version: str, build_data: dict):
        self.app.display_mini_header(self.PLUGIN_NAME)

        self.app.display_waiting("Pre-build artifacts")
        self.app.display_debug(glob(f"{self.project_dir}/*/**"), level=1)
        self.app.display_debug(self.options.asdict(), level=1)
        self.app.display_info("Building c/c++ extensions...")

        self.app.display_info(self.normalized_included_files)
        with self.get_build_dirs() as temp:
            shared_temp_build_dir = os.path.join(temp, "build")
            temp_build_dir = os.path.join(temp, "tmp")
            os.mkdir(shared_temp_build_dir)
            os.mkdir(temp_build_dir)
            self.clean([version])
            setup_file = os.path.join(temp, "setup.py")
            with open(setup_file, "w") as f:
                setup = setup_py(
                    *self.normalized_included_files,
                    options=self.options,
                )
                f.write(setup)

            for opt in self.options.includes:
                if not os.path.exists(opt):
                    msg = "%s does not exist"
                    raise ValueError(msg)

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
            self.app.display_info(glob(f"{self.project_dir}/*/**"))

        if not self.options.retain_intermediate_artifacts:
            self.clean_intermediate()

        build_data["infer_tag"] = True
        build_data["pure_python"] = False
        build_data["artifacts"].extend(self.artifact_patterns)
        build_data["force_include"].update(self.inclusion_map)
        self.app.display_info("Extensions complete")
