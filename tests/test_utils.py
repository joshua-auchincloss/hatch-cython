from src.hatch_cython.utils import memo


def test_memo():
    ran = 0

    class TestC:
        def __init__(self) -> None:
            pass

        @memo
        def do(self):
            nonlocal ran
            ran += 1
            return 42 + ran

        @property
        @memo
        def ok_property(self):
            return "OK"

    tc = TestC()

    assert tc.do() == 43
    assert tc.do() == 43

    tc2 = TestC()
    assert id(tc) != id(tc2)

    assert tc2.do() == 44

    assert tc.ok_property == "OK"
