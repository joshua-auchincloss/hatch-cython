from platform import system


def test_platform_specific():
    sys = system().lower()

    if sys == "windows":
        from example_lib.platform.windows import test_win

        test_win()
    elif sys == "linux":
        from example_lib.platform.linux import test_linux

        test_linux()
    elif sys == "darwin":
        from example_lib.platform.darwin import test_darwin

        test_darwin()
