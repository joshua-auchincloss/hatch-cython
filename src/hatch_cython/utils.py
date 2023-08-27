from collections.abc import Callable

from hatch_cython.types import P, T


def memo(func: Callable[P, T]) -> T:
    value = None
    ran = False

    def wrapped(*args, **kwargs):
        nonlocal value, ran
        if not ran:
            value = func(*args, **kwargs)
            ran = True
        return value

    return wrapped
