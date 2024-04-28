def did_compile():
    return ".so" in __file__ or ".pyd" in __file__ or ".dll" in __file__
