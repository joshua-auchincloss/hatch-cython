import os
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch


def true_if_eq(*vals):
    def inner(v: str, *extra):
        merge = [*vals, *extra]
        ok = any(v == val for val in merge)
        print(f"ok: {v} {ok} ", merge)  # noqa: T201
        return ok

    return inner


true_x64_mac = true_if_eq("/usr/local/include", "/usr/local/lib", "/usr/local/opt")
true_arm_mac = true_if_eq("/opt/homebrew/lib", "/opt/homebrew/include")


@contextmanager
def patch_path(arch: str, *extra: str):
    arches = {
        "x86_64": true_x64_mac,
        "arm64": true_arm_mac,
    }
    h = arches[arch]

    def wrap(path):
        return h(path, *extra)

    with patch("hatch_cython.config.config.path.exists", wrap):
        yield


@contextmanager
def arch_platform(arch: str, platform: str):
    def aarchgetter():
        return arch

    def platformgetter():
        return platform

    try:
        with patch("hatch_cython.utils.plat", platformgetter):
            with patch("hatch_cython.utils.plat", platformgetter):
                with patch("hatch_cython.config.platform.plat", platformgetter):
                    with patch("hatch_cython.plugin.plat", platformgetter):
                        with patch("hatch_cython.utils.aarch", aarchgetter):
                            with patch("hatch_cython.config.platform.aarch", aarchgetter):
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
            "hatch_cython.config.config.import_module",
            get_import,
        ):
            yield
    finally:
        pass


@contextmanager
def override_dir(path: str):
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


@contextmanager
def override_env(d: dict):
    current = os.environ.copy()

    try:
        new = os.environ.copy()
        for k, v in d.items():
            new[k] = v
        os.environ.update(new)
        with patch(
            "hatch_cython.config.flags.environ",
            new,
        ):
            yield
    finally:
        for k, v in current.items():
            os.environ[k] = v
