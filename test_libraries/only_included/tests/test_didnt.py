from src.example_only_included.dont_compile import did_compile


def test_did_not_compile():
    assert not did_compile()
