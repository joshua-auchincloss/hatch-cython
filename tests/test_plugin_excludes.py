import shutil
from sys import path as syspath
from types import SimpleNamespace

import pytest
from toml import load

from hatch_cythonize.plugin import CythonBuildHook

from .test_plugin import join, read
from .utils import override_dir


@pytest.fixture
def new_explicit_proj(tmp_path):
    project_dir = tmp_path / "app"
    project_dir.mkdir()
    (project_dir / "bootstrap.py").write_text(read("test_libraries/bootstrap.py"))
    (project_dir / "pyproject.toml").write_text(read("test_libraries/only_included/pyproject.toml"))
    (project_dir / "hatch.toml").write_text(read("test_libraries/only_included/hatch.toml"))
    (project_dir / "LICENSE.txt").write_text(read("test_libraries/only_included/LICENSE.txt"))
    shutil.copytree(join("test_libraries/only_included", "src"), (project_dir / "src"))
    shutil.copytree(join("test_libraries/only_included", "tests"), (project_dir / "tests"))
    return project_dir


def test_explicit_includes(new_explicit_proj):
    with override_dir(new_explicit_proj):
        syspath.insert(0, str(new_explicit_proj))
        hook = CythonBuildHook(
            new_explicit_proj,
            load(new_explicit_proj / "hatch.toml")["build"]["hooks"]["custom"],
            {},
            SimpleNamespace(name="example_only_included"),
            directory=new_explicit_proj,
            target_name="wheel",
        )
        assert hook.normalized_included_files == ["./src/example_only_included/compile.py"]
        assert hook.options.files.explicit_targets

    syspath.remove(str(new_explicit_proj))
