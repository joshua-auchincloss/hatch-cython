import shutil
from os import getcwd, path
from pathlib import Path  # noqa: F401

import pytest
from toml import load

from hatch_cython.plugin import CythonBuildHook
from hatch_cython.utils import plat

from .utils import arch_platform, override_dir


def join(*rel):
    return path.join(getcwd(), *rel)


def read(rel: str):
    return open(join(*rel.split("/"))).read()


@pytest.fixture
def new_src_proj(tmp_path):
    project_dir = tmp_path / "app"
    project_dir.mkdir()

    (project_dir / "pyproject.toml").write_text(read("test_libraries/src_structure/pyproject.toml"))
    (project_dir / "hatch.toml").write_text(read("test_libraries/src_structure/hatch.toml"))
    (project_dir / "README.md").write_text(read("test_libraries/src_structure/README.md"))
    (project_dir / "LICENSE.txt").write_text(read("test_libraries/src_structure/LICENSE.txt"))
    (project_dir / "bootstrap.py").write_text(read("test_libraries/src_structure/bootstrap.py"))
    shutil.copytree(join("test_libraries/src_structure", "src"), (project_dir / "src"))
    shutil.copytree(join("test_libraries/src_structure", "tests"), (project_dir / "tests"))
    return project_dir


def test_wheel_build_hook(new_src_proj):
    hook = CythonBuildHook(
        new_src_proj,
        load(new_src_proj / "hatch.toml")["build"]["hooks"]["custom"],
        {},
        {},
        directory=new_src_proj,
        target_name="wheel",
    )

    assert hook.is_src

    with arch_platform("", "windows"):
        assert hook.is_windows

    with arch_platform("", "darwin"):
        assert not hook.is_windows

    with arch_platform("", "linux"):
        assert not hook.is_windows

    assert hook.dir_name == "example_lib"

    proj = "./src/example_lib"
    assert hook.project_dir == proj

    assert sorted(hook.precompiled_globs) == sorted(
        [
            "./src/example_lib/*.py",
            "./src/example_lib/**/*.py",
            "./src/example_lib/*.pyx",
            "./src/example_lib/**/*.pyx",
            "./src/example_lib/*.pxd",
            "./src/example_lib/**/*.pxd",
        ]
    )

    with override_dir(new_src_proj):
        hook.clean([])
        build_data = {
            "artifacts": [],
            "force_include": {},
        }
        hook.initialize("0.1.0", build_data)

        assert sorted(hook.normalized_included_files) == sorted(
            [
                "./src/example_lib/__about__.py",
                "./src/example_lib/__init__.py",
                "./src/example_lib/_alias.pyx",
                "./src/example_lib/mod_a/__init__.py",
                "./src/example_lib/mod_a/adds.pyx",
                f"./src/example_lib/platform/{plat()}.pyx",
                "./src/example_lib/mod_a/deep_nest/creates.pyx",
                "./src/example_lib/mod_a/some_defn.pxd",
                "./src/example_lib/mod_a/some_defn.py",
                "./src/example_lib/normal.py",
                "./src/example_lib/templated.pyx",
                "./src/example_lib/test.pyx",
            ]
        )

        assert sorted(
            [{**ls, "files": sorted(ls.get("files"))} for ls in hook.grouped_included_files],
            key=lambda x: x.get("name"),
        ) == [
            {"name": "example_lib.__about__", "files": ["./src/example_lib/__about__.py"]},
            {"name": "example_lib.__init__", "files": ["./src/example_lib/__init__.py"]},
            {"name": "example_lib.aliased", "files": ["./src/example_lib/_alias.pyx"]},
            {"name": "example_lib.mod_a.__init__", "files": ["./src/example_lib/mod_a/__init__.py"]},
            {"name": "example_lib.mod_a.adds", "files": ["./src/example_lib/mod_a/adds.pyx"]},
            {"name": "example_lib.mod_a.deep_nest.creates", "files": ["./src/example_lib/mod_a/deep_nest/creates.pyx"]},
            {"name": "example_lib.mod_a.some_defn", "files": ["./src/example_lib/mod_a/some_defn.py"]},
            {"name": "example_lib.normal", "files": ["./src/example_lib/normal.py"]},
            {"name": f"example_lib.platform.{plat()}", "files": [f"./src/example_lib/platform/{plat()}.pyx"]},
            {"name": "example_lib.templated", "files": ["./src/example_lib/templated.pyx"]},
            {"name": "example_lib.test", "files": ["./src/example_lib/test.pyx"]},
        ]

        rf = sorted(
            [
                "./src/example_lib/__about__.*.pxd",
                "./src/example_lib/__about__.*.py",
                "./src/example_lib/__about__.*.pyx",
                "./src/example_lib/__init__.*.pxd",
                "./src/example_lib/__init__.*.py",
                "./src/example_lib/__init__.*.pyx",
                "./src/example_lib/_alias.*.pxd",
                "./src/example_lib/_alias.*.py",
                "./src/example_lib/_alias.*.pyx",
                "./src/example_lib/mod_a/__init__.*.pxd",
                "./src/example_lib/mod_a/__init__.*.py",
                "./src/example_lib/mod_a/__init__.*.pyx",
                "./src/example_lib/mod_a/adds.*.pxd",
                "./src/example_lib/mod_a/adds.*.py",
                "./src/example_lib/mod_a/adds.*.pyx",
                "./src/example_lib/mod_a/deep_nest/creates.*.pxd",
                "./src/example_lib/mod_a/deep_nest/creates.*.py",
                "./src/example_lib/mod_a/deep_nest/creates.*.pyx",
                "./src/example_lib/mod_a/some_defn.*.pxd",
                "./src/example_lib/mod_a/some_defn.*.pxd",
                "./src/example_lib/mod_a/some_defn.*.py",
                "./src/example_lib/mod_a/some_defn.*.py",
                "./src/example_lib/mod_a/some_defn.*.pyx",
                "./src/example_lib/mod_a/some_defn.*.pyx",
                "./src/example_lib/normal.*.pxd",
                "./src/example_lib/normal.*.py",
                "./src/example_lib/normal.*.pyx",
                "./src/example_lib/templated.*.pxd",
                "./src/example_lib/templated.*.py",
                "./src/example_lib/templated.*.pyx",
                f"./src/example_lib/platform/{plat()}.*.pxd",
                f"./src/example_lib/platform/{plat()}.*.py",
                f"./src/example_lib/platform/{plat()}.*.pyx",
                "./src/example_lib/test.*.pxd",
                "./src/example_lib/test.*.py",
                "./src/example_lib/test.*.pyx",
            ]
        )
        assert sorted(hook.normalized_dist_globs) == rf
        assert build_data.get("infer_tag")
        assert not build_data.get("pure_python")
        assert sorted(hook.artifacts) == sorted(build_data.get("artifacts")) == sorted([f"/{f}" for f in rf])
        assert len(build_data.get("force_include")) == 11
