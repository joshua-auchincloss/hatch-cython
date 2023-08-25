from hatch_cython.config import Config
from hatch_cython.plugin import setup_py


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

if __name__ == "__main__":
    exts = [
    Extension("*", [
                "./abc/def.pyx"
            ],
            extra_compile_args=COMPILEARGS,
            include_dirs=INCLUDES,
            libraries=LIBRARIES,
            library_dirs=LIBRARY_DIRS,

        ),
    ]
    ext_modules = cythonize(
            exts,
            compiler_directives=DIRECTIVES,
            include_path=INCLUDES
    )
    setup(ext_modules=ext_modules)
""".strip()


def test_setup_py():
    cfg = Config(
        includes=["/123"],
        libraries=["/abc"],
        library_dirs=["/def"],
    )
    assert clean(
        setup_py(
            "./abc/def.pyx",
            options=cfg,
        )
    ) == clean(EXPECT)
