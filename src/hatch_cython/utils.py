import os
import platform
from textwrap import dedent

from Cython import __version__ as __cythonversion__

from hatch_cython.__about__ import __version__
from hatch_cython.constants import NORM_GLOB, UAST
from hatch_cython.types import CallableT, P, T, UnionT


def stale(src: str, dest: str):
    if not os.path.exists(src) and os.path.exists(dest):
        return True
    return os.path.getmtime(src) > os.path.getmtime(dest)


def memo(func: CallableT[P, T]) -> CallableT[P, T]:
    keyed = {}

    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        nonlocal keyed

        # if we have a class, memo will reserve objects between
        # instances, so we need to key this by the id of the instance
        # note: dont call  hasattr here because hasattr is pretty much
        # a try catch for property access - ergo we get infinite recursive
        # calls if a property is memoed
        if len(args) and func.__name__ in dir(args[0]):
            idof = id(args[0])
        else:
            idof = None

        if idof not in keyed:
            keyed[idof] = func(*args, **kwargs)
        return keyed[idof]

    return wrapped


@memo
def plat():
    return platform.system().lower()


@memo
def aarch():
    return platform.machine().lower()


def options_kws(kwds: dict):
    return ",\n\t".join((f"{k}={v!r}" for k, v in kwds.items()))


def parse_user_glob(
    uglob: str,
    variant: UnionT[None, str] = None,
    modifier: UnionT[CallableT[[str], str], None] = None,
):
    if variant is None:
        variant = NORM_GLOB
    pre = uglob.replace("\\*", UAST)
    if modifier:
        pre = modifier(pre)
    imd = pre.replace("*", variant)
    return imd.replace(UAST, "*")


@memo
def path_delim() -> str:
    if plat() == "windows":
        return ";"
    return ":"


def autogenerated(keywords: dict):
    return dedent(
        f"""# DO NOT EDIT.
# Autoformatted by hatch-cython.
# Version: {__version__}
# Cython: {__cythonversion__}
# Platform: {plat()}
# Architecture: {aarch()}
# Keywords: {keywords!r}
"""
    )
