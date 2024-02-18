from example_lib.custom_includes import bwfpy


def test_custom_includes():
    assert bwfpy(4) == 20
