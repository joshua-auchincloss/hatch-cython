from contextlib import contextmanager
from unittest.mock import patch


def true_if_eq(*vals):
    def inner(v):
        return any(v == val for val in vals)

    return inner


@contextmanager
def arch_platform(arch: str, platform: str):
    def aarchgetter():
        # if arch == "arm64" and platform == 'windows':
        #     raise ValueError(arch)
        return arch

    def platformgetter():
        return platform

    try:
        with patch("hatch_cython.config.aarch", aarchgetter):
            with patch("hatch_cython.config.plat", platformgetter):
                yield
    finally:
        print(f"Clean {arch}-{platform}")  # noqa: T201
        del aarchgetter, platformgetter
        pass
