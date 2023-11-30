from numpy import linspace, longlong

from example_lib.test import hello_numpy, hello_world


def test_hello_world():
    assert hello_world("world") == "hello, world"


def test_hello_numpy():
    assert hello_numpy(linspace(0, 100, 25, dtype=longlong)) == 1240
