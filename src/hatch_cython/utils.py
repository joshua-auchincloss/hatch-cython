import platform

from hatch_cython.constants import NORM_GLOB, UAST
from hatch_cython.types import CallableT, P, T


def memo(func: CallableT[P, T]) -> CallableT[P, T]:
    value = None
    ran = False

    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        nonlocal value, ran
        if not ran:
            value = func(*args, **kwargs)
            ran = True
        return value

    return wrapped


@memo
def plat():
    return platform.system().lower()


@memo
def aarch():
    return platform.machine().lower()


def options_kws(kwds: dict):
    return ",\n\t".join((f"{k}={v!r}" for k, v in kwds.items()))


def parse_user_glob(uglob: str):
    return uglob.replace("\\*", UAST).replace("*", NORM_GLOB).replace(UAST, "*")
