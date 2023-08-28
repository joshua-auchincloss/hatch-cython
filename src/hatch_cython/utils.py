from hatch_cython.types import P, T, callable_t


def memo(func: callable_t[P, T]) -> T:
    value = None
    ran = False

    def wrapped(*args, **kwargs):
        nonlocal value, ran
        if not ran:
            value = func(*args, **kwargs)
            ran = True
        return value

    return wrapped
