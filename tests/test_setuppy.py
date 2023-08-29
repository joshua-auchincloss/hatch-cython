import ast
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
EXTENSIONS = [{'name': 'abc.def', 'files': ['./abc/def.pyx']},{'name': 'abc.depb', 'files': ['./abc/depb.py']}]
LINKARGS = ['-I/etc/abc/linka.h']

if __name__ == "__main__":
    exts = [
        Extension(  ex.get("name"),
                    ex.get("files"),
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
    with patch("hatch_cython.config.config.path.exists", true_if_eq()):
        with arch_platform("x86_64", ""):
            setup = setup_py(
                {"name": "abc.def", "files": ["./abc/def.pyx"]},
                {"name": "abc.depb", "files": ["./abc/depb.py"]},
                options=cfg,
            )
    assert clean(setup) == clean(EXPECT)


def test_solo_ext_type_validations():
    cfg = Config(
        includes=["/123"],
        libraries=["/abc"],
        library_dirs=["/def"],
        cythonize_kwargs={"abc": "def"},
        extra_link_args=[PlatformArgs(arg="-I/etc/abc/linka.h")],
    )
    with patch("hatch_cython.config.config.path.exists", true_if_eq()):
        with arch_platform("x86_64", ""):
            setup = setup_py(
                {"name": "abc.def", "files": ["./abc/def.pyx"]},
                options=cfg,
            )
    tested = False
    exteq = "EXTENSIONS ="
    for ln in setup.splitlines():
        if ln.startswith(exteq):
            tested = True
            ext = ast.literal_eval(ln.replace(exteq, "").strip())
            assert isinstance(ext, list)
            for ex in ext:
                assert isinstance(ex, dict)
                assert isinstance(ex.get("name"), str)
                assert isinstance(ex.get("files"), list)

    if not tested:
        raise ValueError(setup, tested, "missed test")
