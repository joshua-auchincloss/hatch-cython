from pytest import raises

from hatch_cython.config.autoimport import Autoimport
from hatch_cython.config.includes import parse_includes


def test_includes():
    parse = {
        "pkg": "somelib",
        "include": "gets_include",
        "libraries": "gets_libraries",
        "library_dirs": "gets_library_dirs",
        "required_call": "some_setup_op",
    }
    ok = parse_includes(
        "include_abc",
        parse,
    )
    assert ok == Autoimport(**parse)
    ok = parse_includes(
        "include_abc",
        "some_attr",
    )
    assert ok == Autoimport(pkg="abc", include="some_attr")


def test_invalid():
    with raises(ValueError, match="either provide a known package"):
        parse_includes("list", [])
