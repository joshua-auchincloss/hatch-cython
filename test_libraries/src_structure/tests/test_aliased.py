def test_aliased():
    from example_lib.aliased import some_aliased

    assert some_aliased("abc") == "abc"
