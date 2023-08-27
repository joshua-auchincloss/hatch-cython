from unittest.mock import patch

from hatch_cython.config import Config, PlatformArgs
from hatch_cython.plugin import setup_py

from .utils import arch_platform, true_if_eq


def clean(s: str):
    return "\n".join(v.strip() for v in s.splitlines() if v.strip() != "")


EXPECT = """
from setuptools import Extension, setup
from Cython.Build import cythonize

COMPILEARGS = ['-O2']
DIRECTIVES = {'binding': True, 'language_level': 3}
INCLUDES = ['/123']
LIBRARIES = ['/abc']
LIBRARY_DIRS = ['/def']
EXTENSIONS = (['./abc/def.pyx'],['./abc/depb.py'])
LINKARGS = ['-I/etc/abc/linka.h']

if __name__ == "__main__":
    exts = [
        Extension("*",
                    ex,
                    extra_compile_args=COMPILEARGS,
                    extra_link_args=LINKARGS,
                    include_dirs=INCLUDES,
                    libraries=LIBRARIES,
                    library_dirs=LIBRARY_DIRS,

        ) for ex in EXTENSIONS
    ]
    ext_modules = cythonize(
            exts,
            compiler_directives=DIRECTIVES,
            include_path=INCLUDES,
            abc='def'
    )
    setup(ext_modules=ext_modules)
""".strip()


def test_setup_py():
    cfg = Config(
        includes=["/123"],
        libraries=["/abc"],
        library_dirs=["/def"],
        cythonize_kwargs={"abc": "def"},
        extra_link_args=[PlatformArgs(arg="-I/etc/abc/linka.h")],
    )
    with patch("hatch_cython.config.path.exists", true_if_eq()):
        with arch_platform("x86_64", ""):
            setup = setup_py(
                ["./abc/def.pyx"],
                ["./abc/depb.py"],
                options=cfg,
            )
    assert clean(setup) == clean(EXPECT)
