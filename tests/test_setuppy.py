from hatch_cython.plugin import setup_py


def clean(s: str):
    return "\n".join(v.strip() for v in s.splitlines() if v.strip() != "")


EXPECT = """
from setuptools import Extension, setup
from Cython.Build import cythonize

COMPILEARGS = ['-O2']
DIRECTIVES = {'binding': True, 'language_level': 3}

if __name__ == "__main__":
    exts = [
    Extension("*", [
                "./abc/def.pyx"
            ],
            extra_compile_args=COMPILEARGS,

        ),
    ]
    ext_modules = cythonize(exts, compiler_directives=DIRECTIVES)
    setup(ext_modules=ext_modules)
""".strip()


def test_setup_py():
    assert clean(setup_py("./abc/def.pyx")) == clean(EXPECT)
