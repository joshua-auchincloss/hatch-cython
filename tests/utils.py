from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch


def true_if_eq(*vals):
    def inner(v):
        return any(v == val for val in vals)

    return inner


true_x64_mac = true_if_eq("/usr/local/include", "/usr/local/lib")
true_arm_mac = true_if_eq("/opt/homebrew/lib", "/opt/homebrew/include")


@contextmanager
def patch_path(arch: str):
    arches = {
        "x86_64": true_x64_mac,
        "arm64": true_arm_mac,
    }
    with patch("hatch_cython.config.path.exists", arches[arch]):
        yield


@contextmanager
def arch_platform(arch: str, platform: str):
    def aarchgetter():
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


@contextmanager
def pyversion(maj="3", min="10", p="0"):  # noqa: A002
    try:
        with patch("platform.python_version_tuple", lambda: (maj, min, p)):
            yield
    finally:
        pass


@contextmanager
def import_module(gets_include, gets_libraries=None, gets_library_dirs=None, some_setup_op=None):
    def get_import(name: str):
        print(f"patched {name}")  # noqa: T201
        return SimpleNamespace(
            gets_include=gets_include,
            gets_libraries=gets_libraries,
            gets_library_dirs=gets_library_dirs,
            some_setup_op=some_setup_op,
        )

    try:
        with patch(
            "hatch_cython.config.import_module",
            get_import,
        ):
            yield
    finally:
        pass
