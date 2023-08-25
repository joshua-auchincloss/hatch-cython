from textwrap import dedent
from types import SimpleNamespace
from unittest.mock import patch

from toml import loads

from hatch_cython.config import parse_from_dict

data = """
[options]
includes = []
include_numpy = false
include_pyarrow = false

include_somelib = { pkg = "somelib", include = "gets_include", libraries = "gets_libraries", library_dirs = "gets_library_dirs", required_call = "some_setup_op" }

compile_args = [{ platforms = ["nt"], arg = "-std=c++17" }, { platforms = "posix", arg = "-I/abc/def" } ]

directives = { boundscheck = false, nonecheck = false, language_level = 3, binding = true }

abc_compile_kwarg = "test"
"""  # noqa: E501


def test_config_parser():
    parsed = loads(dedent(data))

    def get_include():
        return "abc"

    def gets_libraries():
        return ["lib-a"]

    def gets_library_dirs():
        return ["dir-a"]

    ran = False

    def some_setup_op():
        nonlocal ran
        ran = True

    with patch(
        "hatch_cython.config.import_module",
        (
            lambda _: SimpleNamespace(
                gets_include=get_include,
                gets_libraries=gets_libraries,
                gets_library_dirs=gets_library_dirs,
                some_setup_op=some_setup_op,
            )
        ),
    ):
        cfg = parse_from_dict(SimpleNamespace(config=parsed))
        assert ran

    assert cfg.compile_args

    with patch("hatch_cython.config.name", "nt"):
        assert cfg.compile_args_for_platform == ["-std=c++17"]
    with patch("hatch_cython.config.name", "posix"):
        assert cfg.compile_args_for_platform == ["-I/abc/def"]

    assert cfg.directives == {"boundscheck": False, "nonecheck": False, "language_level": 3, "binding": True}

    assert cfg.libraries == gets_libraries()
    assert cfg.library_dirs == gets_library_dirs()
    assert get_include() in cfg.includes
    assert cfg.compile_kwargs == {"abc_compile_kwarg": "test"}
