from time import sleep

import pytest

from src.hatch_cythonize.utils import memo, stale


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

    # mtime may not be within resolution to run tests consistently, so we need to wait for sys
    # to reflect the modification times
    # https://stackoverflow.com/questions/19059877/python-os-path-getmtime-time-not-changing
    sleep(5)

    dest.write_text("hello world")

    sleep(5)

    assert not stale(
        str(src),
        str(dest),
    )

    with src.open("w") as f:
        f.write("now stale")

    sleep(5)

    assert stale(
        str(src),
        str(dest),
    )

    dest.unlink()

    sleep(5)

    assert stale(
        str(src),
        str(dest),
    )
