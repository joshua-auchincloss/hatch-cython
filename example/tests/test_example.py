from numpy import arange, int64

from example.test import hello_numpy, hello_world


def test_hello_world():
    assert hello_world("world") == "hello, world"


def test_hello_numpy():
    assert hello_numpy(arange(0, 100, 2, dtype=int64)) == 2450
