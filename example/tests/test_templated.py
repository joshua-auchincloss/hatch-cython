from example_lib.templated import cfpow, ciadd, cipow


def test_template_ops():
    assert ciadd(1, 2) == 3
    assert cipow(2, 2) == 4
    assert cfpow(5.5, 2) == 30.25
