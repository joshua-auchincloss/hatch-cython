from pytest import raises

from hatch_cython.config.platform import PlatformArgs, parse_platform_args, parse_to_plat


def test_platform():
    out = [{"arg": "a"}, "b"]
    parse_to_plat(PlatformArgs, {"arg": "a"}, out, 0, False)
    assert out[0] == PlatformArgs(
        platforms="*", arch="*", depends_path=False, marker=None, apply_to_marker=None, arg="a"
    )
    assert out[1] == "b"

    parsed = parse_platform_args(
        {
            "some": [{"arg": "a"}, "b"],
        },
        "some",
        lambda: [],
    )
    assert parsed == out


def test_invalid_platform():
    with raises(ValueError, match="arg 0 is invalid"):
        parse_to_plat(PlatformArgs, "a", ["a"], 0, True)
