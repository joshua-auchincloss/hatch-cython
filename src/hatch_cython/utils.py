from hatch_cython.types import P, T, callable_t


def memo(func: callable_t[P, T]) -> callable_t[P, T]:
    value = None
    ran = False

    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        nonlocal value, ran
        if not ran:
            value = func(*args, **kwargs)
            ran = True
        return value

    return wrapped
