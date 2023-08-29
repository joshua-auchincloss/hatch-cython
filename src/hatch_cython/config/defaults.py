from hatch_cython.config.platform import PlatformArgs
from hatch_cython.constants import POSIX_CORE


def get_default_link():
    return [
        PlatformArgs(arg="-L/opt/homebrew/lib", platforms=POSIX_CORE, depends_path=True),
        PlatformArgs(arg="-L/usr/local/lib", platforms=POSIX_CORE, depends_path=True),
        PlatformArgs(arg="-L/usr/local/opt", platforms=POSIX_CORE, depends_path=True),
    ]


def get_default_compile():
    return [
        PlatformArgs(arg="-O2"),
        PlatformArgs(arg="-I/opt/homebrew/include", platforms=POSIX_CORE, depends_path=True),
        PlatformArgs(arg="-I/usr/local/include", platforms=POSIX_CORE, depends_path=True),
    ]
