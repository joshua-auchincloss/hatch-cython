from typing import TypedDict

from hatch_cython.config import Config
from hatch_cython.types import ListStr, ListT
from hatch_cython.utils import options_kws


class ExtensionArg(TypedDict):
    name: str
    files: ListStr


def setup_py(
    *files: ListT[ListStr],
    options: Config,
    sdist: bool,
):
    code = """
import os
import sys

if sys.platform == "win32":
    compiler_override = os.environ.get("CC") or os.environ.get("CXX")
    if compiler_override:
        for mod_name in ("distutils.compilers.C.msvc", "setuptools._distutils.compilers.C.msvc"):
            try:
                mod = __import__(mod_name, fromlist=["Compiler", "_find_exe"])
                orig_init = mod.Compiler.initialize
                _find_exe = getattr(mod, "_find_exe", None)

                def patched_init(self, plat_name=None, _orig=orig_init, _cc=compiler_override, _find=_find_exe):
                    _orig(self, plat_name)
                    if _find and hasattr(self, "_paths"):
                        paths = self._paths.split(os.pathsep)
                        exe = _cc if _cc.lower().endswith(".exe") else f"{{_cc}}.exe"
                        found = _find(exe, paths)
                        if found != exe or os.path.isfile(_cc):
                            self.cc = found
                        else:
                            self.cc = _cc
                    else:
                        self.cc = _cc

                mod.Compiler.initialize = patched_init
            except (ImportError, AttributeError):
                pass

from setuptools import Extension, setup
from Cython.Build import cythonize

INCLUDES = {includes!r}
EXTENSIONS = {ext_files!r}

if __name__ == "__main__":
    exts = [
        Extension(  ex.get("name"),
                    ex.get("files"),
                    extra_compile_args={compile_args!r},
                    extra_link_args={extra_link_args!r},
                    include_dirs=INCLUDES,
                    libraries={libs!r},
                    library_dirs={lib_dirs!r},
                    define_macros={define_macros!r},
                    {keywords}
        ) for ex in EXTENSIONS
    ]
    ext_modules = cythonize(
            exts,
            compiler_directives={directives!r},
            include_path=INCLUDES,
            {cython}
    )

"""
    if not sdist:
        code += """
    setup(ext_modules=ext_modules)
        """

    kwds = options_kws(options.compile_kwargs)
    cython = options_kws(options.cythonize_kwargs)
    return code.format(
        compile_args=options.compile_args_for_platform,
        extra_link_args=options.compile_links_for_platform,
        directives=options.directives,
        ext_files=files,
        keywords=kwds,
        cython=cython,
        includes=options.includes,
        libs=options.libraries,
        lib_dirs=options.library_dirs,
        define_macros=options.define_macros,
    ).strip()
