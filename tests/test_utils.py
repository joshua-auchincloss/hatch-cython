import pytest

from src.hatch_cython.utils import memo, stale


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


@pytest.fixture
def new_tmp_dir(tmp_path):
    project_dir = tmp_path / "app"
    project_dir.mkdir()
    return project_dir


def test_stale(new_tmp_dir):
    src = new_tmp_dir / "test.txt"
    dest = new_tmp_dir / "dest.txt"
    src.write_text("hello world")
    dest.write_text("hello world")

    assert not stale(
        str(src),
        str(dest),
    )

    src.write_text("now stale")
    assert stale(
        str(src),
        str(dest),
    )

    dest.unlink()
    assert stale(
        str(src),
        str(dest),
    )
