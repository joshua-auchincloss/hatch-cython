from pytest import raises

from hatch_cython.config.macros import parse_macros


def test_macros():
    test_ok = [
        ["NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"],
        ["ABC_DEF"],
        ["GHI_JKL"],
    ]
    assert parse_macros(test_ok) == [
        ("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"),
        ("ABC_DEF", None),
        ("GHI_JKL", None),
    ]


def test_invalid():
    test_not_ok = [
        # extra value
        ["a", "b", "c"]
    ]
    with raises(
        ValueError,
        match="macros must be defined",
    ):
        parse_macros(test_not_ok)
