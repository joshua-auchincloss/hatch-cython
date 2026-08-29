import sys
from os import getcwd
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import PropertyMock, patch

from hatch_cython.plugin import CythonBuildHook

from .utils import arch_platform


def test_limited_api_tag():
    # Mocking minimum to be 3.8 (0x03080000)
    options = {"options": {"py_limited_api": True, "define_macros": [["Py_LIMITED_API", "0x03080000"]]}}

    with patch("hatch_cython.plugin.sys_tags") as mock_tags:
        mock_tag = SimpleNamespace(platform="win_amd64")
        mock_tags.return_value = iter([mock_tag])

        root = Path(getcwd())
        hook = CythonBuildHook(
            root,
            options,
            {},
            SimpleNamespace(name="example_lib"),
            directory=root,
            target_name="wheel",
        )

        tag = hook._limited_api_tag()
        assert tag == "cp38-abi3-win_amd64"


def test_limited_api_tag_no_macro():
    options = {"options": {"py_limited_api": True}}

    with patch("hatch_cython.plugin.sys_tags") as mock_tags:
        mock_tag = SimpleNamespace(platform="win_amd64")
        mock_tags.return_value = iter([mock_tag])

        root = Path(getcwd())
        hook = CythonBuildHook(
            root,
            options,
            {},
            SimpleNamespace(name="example_lib"),
            directory=root,
            target_name="wheel",
        )

        major, minor = sys.version_info.major, sys.version_info.minor
        tag = hook._limited_api_tag()
        assert tag == f"cp{major}{minor}-abi3-win_amd64"


def test_limited_api_disabled():
    options = {"options": {"py_limited_api": False}}

    root = Path(getcwd())
    hook = CythonBuildHook(
        root,
        options,
        {},
        SimpleNamespace(name="example_lib"),
        directory=root,
        target_name="wheel",
    )

    tag = hook._limited_api_tag()
    assert tag is None


def test_initialize_with_limited_api():
    options = {"options": {"py_limited_api": True, "define_macros": [["Py_LIMITED_API", "0x03090000"]]}}

    with arch_platform("x86_64", "linux"):
        with patch("hatch_cython.plugin.sys_tags") as mock_tags:
            mock_tag = SimpleNamespace(platform="linux_x86_64")
            mock_tags.return_value = iter([mock_tag])

            root = Path(getcwd())
            hook = CythonBuildHook(
                root,
                options,
                {},
                SimpleNamespace(name="example_lib"),
                directory=root,
                target_name="wheel",
            )

            # Mocking build_ext and grouped_included_files
            with (
                patch.object(CythonBuildHook, "build_ext"),
                patch.object(CythonBuildHook, "grouped_included_files", new_callable=PropertyMock) as mock_grouped,
            ):
                mock_grouped.return_value = []
                build_data = {"artifacts": [], "force_include": {}}
                hook.initialize("0.1.0", build_data)

                assert build_data["infer_tag"] is False
                assert build_data["tag"] == "cp39-abi3-linux_x86_64"
