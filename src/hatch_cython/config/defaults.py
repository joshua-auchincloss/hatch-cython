from subprocess import CalledProcessError, check_output

from hatch_cython.config.platform import PlatformArgs
from hatch_cython.constants import POSIX_CORE
from hatch_cython.utils import aarch, memo, plat

BREW = "brew"


# pragma: no cover
@memo
def brew_path():
    if plat() == "darwin":
        # no user input - S603 is false positive
        try:
            proc = check_output([BREW, "--prefix"])  # noqa: S603
        except CalledProcessError:
            proc = None
        dec = proc.decode().replace("\n", "") if proc else None
        if dec and dec != "":
            return dec
        return "/opt/homebrew" if aarch() == "arm64" else "/usr/local"


def get_default_link():
    base = [
        PlatformArgs(arg="-L/usr/local/lib", platforms=POSIX_CORE, depends_path=True),
        PlatformArgs(arg="-L/usr/local/opt", platforms=POSIX_CORE, depends_path=True),
    ]

    brew = brew_path()
    if brew:
        base.extend(
            [
                PlatformArgs(arg=f"-L{brew}/opt", platforms=POSIX_CORE, depends_path=True),
                PlatformArgs(arg=f"-L{brew}/lib", platforms=POSIX_CORE, depends_path=True),
            ]
        )
    return base


def get_default_compile():
    base = [
        PlatformArgs(arg="-O2"),
        PlatformArgs(arg="-I/usr/local/include", platforms=POSIX_CORE, depends_path=True),
    ]
    brew = brew_path()
    if brew:
        base.extend(
            [
                PlatformArgs(arg=f"-I{brew}/include", platforms=POSIX_CORE, depends_path=True),
            ]
        )
    return base
