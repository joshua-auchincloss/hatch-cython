def test_muls():
    from example_lib.mod_a.adds import fmul, imul

    assert fmul(5.5, 5.5) == 30.25
    assert imul(21, 2) == 42


def test_vals():
    from example_lib.mod_a.some_defn import ValueDefn

    v = ValueDefn(10)
    assert v.value == 10
    v.set(5)
    assert v.value == 5


def test_deep_nesting():
    from example_lib.mod_a.deep_nest.creates import fast_create

    o = fast_create()
    assert o.do() == "abc"
