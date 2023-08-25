from example_lib.mod_a.adds import fmul, imul


def test_muls():
    assert fmul(5.5, 5.5) == 30.25
    assert imul(21, 2) == 42
