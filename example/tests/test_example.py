from numpy import arange

from example.test import hello_numpy, hello_world


def test_hello_world():
    assert hello_world("world") == "hello, world"


def test_hello_numpy():
    hello_numpy(arange(100))
