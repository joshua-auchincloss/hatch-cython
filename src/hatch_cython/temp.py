from typing import TypedDict

from hatch_cython.config import Config
from hatch_cython.types import ListStr, list_t
from hatch_cython.utils import options_kws


class ExtensionArg(TypedDict):
    name: str
    files: ListStr


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
EXTENSIONS = [{ext_files}]
LINKARGS = {extra_link_args}

if __name__ == "__main__":
    exts = [
        Extension(  ex.get("name"),
                    ex.get("files"),
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
