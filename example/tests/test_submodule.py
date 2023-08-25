from example_lib.mod_a.adds import fmul, imul
from example_lib.mod_a.some_defn import ValueDefn


def test_muls():
    assert fmul(5.5, 5.5) == 30.25
    assert imul(21, 2) == 42


def test_vals():
    v = ValueDefn(10)
    assert v.value == 10
    v.set(5)
    assert v.value == 5
