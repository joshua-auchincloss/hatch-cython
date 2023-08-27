import os
import subprocess
import sys
from contextlib import contextmanager
from glob import glob
from tempfile import TemporaryDirectory
from typing import ClassVar

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from hatch_cython.config import Config, parse_from_dict, plat
from hatch_cython.types import ListStr, list_t


def options_kws(kwds: dict):
    return ",\n\t".join((f"{k}={v!r}" for k, v in kwds.items()))


def setup_py(
    *files: list_t[ListStr],
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
EXTENSIONS = ({ext_files})
LINKARGS = {extra_link_args}

if __name__ == "__main__":
    exts = [
        Extension("*",
                    ex,
                    extra_compile_args=COMPILEARGS,
                    extra_link_args=LINKARGS,
                    include_dirs=INCLUDES,
                    libraries=LIBRARIES,
                    library_dirs=LIBRARY_DIRS,
                    {keywords}
        ) for ex in EXTENSIONS
    ]
    ext_modules = cythonize(
            exts,
            compiler_directives=DIRECTIVES,
            include_path=INCLUDES,
            {cython}
    )
    setup(ext_modules=ext_modules)
"""
    ext_files = ",".join([repr(lf) for lf in files])
    kwds = options_kws(options.compile_kwargs)
    cython = options_kws(options.cythonize_kwargs)
    return code.format(
        compile_args=repr(options.compile_args_for_platform),
        extra_link_args=repr(options.compile_links_for_platform),
        directives=repr(options.directives),
        ext_files=ext_files,
        keywords=kwds,
        cython=cython,
        includes=repr(options.includes),
        libs=repr(options.libraries),
        lib_dirs=repr(options.library_dirs),
    ).strip()


class CythonBuildHook(BuildHookInterface):
    PLUGIN_NAME = "cython"

    precompiled_extension: ClassVar[list] = [
        ".pyx",
        ".pxd",
    ]
    intermediate_extensions: ClassVar[list] = [
        ".c",
        ".cpp",
    ]
    compiled_extensions: ClassVar[list] = [
        ".dll",
        # unix
        ".so",
        # windows
        ".pyd",
    ]

    _config: Config
    _dir: str
    _included: ListStr
    _artifact_patterns: ListStr
    _artifact_globs: ListStr
    _norm_included_files: ListStr
    _norm_artifact_patterns: ListStr
    _grouped_norm: list_t[ListStr]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._included = None
        self._norm_included_files = None
        self._artifact_patterns = None
        self._artifact_globs = None
        self._norm_artifact_patterns = None
        self._config = None
        self._dir = None
        self._grouped_norm = None

    @property
    def is_src(self):
        return os.path.exists(os.path.join(self.root, "src"))

    @property
    def is_windows(self):
        return plat() == "windows"

    def normalize_path(self, pattern: str):
        if self.is_windows:
            return pattern.replace("/", "\\")
        return pattern.replace("\\", "/")

    def normalize_glob(self, pattern: str):
        return pattern.replace("\\", "/")

    @property
    def dir_name(self):
        return self.options.src if self.options.src is not None else self.metadata.name

    @property
    def project_dir(self):
        if self._dir is None:
            if self.is_src:
                src = f"./src/{self.dir_name}"
            else:
                src = f"./{self.dir_name}"
            self._dir = src
        return self._dir

    @property
    def precompiled_globs(self):
        _globs = []
        for ex in self.precompiled_extension:
            _globs.extend((f"{self.project_dir}/*{ex}", f"{self.project_dir}/**/*{ex}"))
        return _globs

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
    def grouped_included_files(self) -> list_t[ListStr]:
        if self._grouped_norm is None:
            grouped = {}
            for norm in self.normalized_included_files:
                root, ext = os.path.splitext(norm)
                ok = True
                if ext == ".pxd":
                    pyfile = norm.replace(".pxd", ".py")
                    if os.path.exists(pyfile):
                        norm = pyfile  # noqa: PLW2901
                    else:
                        ok = False
                        self.app.display_warning(f"attempted to use .pxd file without .py file ({norm})")
                if grouped.get(root) and ok:
                    grouped[root].append(norm)
                elif ok:
                    grouped[root] = [norm]
            self._grouped_norm = list(grouped.values())
        return self._grouped_norm

    @property
    def artifact_globs(self):
        if self._artifact_globs is None:
            artifact_globs = []
            for included_file in self.normalized_included_files:
                root, _ = os.path.splitext(included_file)
                artifact_globs.extend(f"{root}.*{ext}" for ext in self.precompiled_extension)
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

    def _globs(self, exts: ListStr):
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

    def rm_recurse(self, li: ListStr):
        for f in li:
            os.remove(f)

    def clean_intermediate(self):
        self.rm_recurse(self.intermediate)

    def clean_compiled(self):
        self.rm_recurse(self.compiled)

    def clean(self, _versions: ListStr):
        self.clean_intermediate()
        self.clean_compiled()

    @property
    def options(self):
        if self._config is None:
            self._config = parse_from_dict(self)
        return self._config

    def initialize(self, version: str, build_data: dict):
        self.app.display_mini_header(self.PLUGIN_NAME)
        self.app.display_debug("Options")
        self.app.display_debug(self.options.asdict(), level=1)

        self.app.display_waiting("Pre-build artifacts")
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
                    *self.grouped_included_files,
                    options=self.options,
                )
                f.write(setup)

            self.options.validate_include_opts()

            process = subprocess.run(  # noqa: PLW1510
                [  # noqa: S603
                    sys.executable,
                    setup_file,
                    "build_ext",
                    "--inplace",
                    "--verbose",
                    "--build-lib",
                    shared_temp_build_dir,
                    "--build-temp",
                    temp_build_dir,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=self.options.envflags.env,
            )
            if process.returncode:
                self.app.display_error(f"cythonize exited non null status {process.returncode}")
                self.app.display_error(process.stdout.decode("utf-8"))
                msg = "failed compilation"
                raise Exception(msg)

            self.app.display_info(process.stdout.decode("utf-8"))

            self.app.display_success("Post-build artifacts")
            self.app.display_info(glob(f"{self.project_dir}/*/**"))

        if not self.options.retain_intermediate_artifacts:
            self.clean_intermediate()

        build_data["infer_tag"] = True
        build_data["pure_python"] = False
        build_data["artifacts"].extend(self.artifact_patterns)
        build_data["force_include"].update(self.inclusion_map)
        self.app.display_info("Extensions complete")
