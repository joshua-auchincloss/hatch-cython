from platform import system

from example_lib.templated import ciadd, cipow

PLAT = system().lower()


def test_template_ops():
    assert ciadd(1, 2) == 3
    assert cipow(2, 2) == 4

    if PLAT in ("windows", "darwin"):
        from example_lib.templated import cfpow

        assert cfpow(5.5, 2) == 30.25
    if PLAT == "windows":
        from example_lib.templated import ccadd

        assert ccadd(complex(real=4, imag=2), complex(real=2, imag=0)) == complex(real=6, imag=2)
