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
