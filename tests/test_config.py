from textwrap import dedent
from types import SimpleNamespace
from unittest.mock import patch

from toml import loads

from hatch_cython.config import parse_from_dict
from hatch_cython.config.defaults import brew_path
from hatch_cython.utils import aarch, plat

from .utils import arch_platform, import_module, patch_brew, patch_path, pyversion


def test_brew_path():
    if plat() == "darwin" and aarch() == "x86_64":
        assert brew_path() == "/usr/local"
    elif plat() == "darwin" and aarch() == "arm64":
        assert brew_path() == "/opt/homebrew"
    else:
        assert brew_path() is None


def test_brew_fails_safely():
    with patch("hatch_cython.config.defaults.BREW", "some-cmd-that-doesnt-exist"):
        with patch("hatch_cython.utils.memo", lambda f: f):
            with arch_platform("x86_64", "darwin", brew=False):
                assert brew_path() == "/usr/local"
            with arch_platform("arm64", "darwin", brew=False):
                assert brew_path() == "/opt/homebrew"


def test_config_with_brew():
    with pyversion("3", "9"), arch_platform("arm64", "darwin"), patch_path("arm64"), patch_brew("/opt/homebrew"):
        ok = parse_from_dict(SimpleNamespace(config={"options": {"parallel": True}}))
        assert sorted(ok.compile_args_for_platform) == sorted(["-O2", "-I/opt/homebrew/include"])
        assert ok.compile_links_for_platform == ["-L/opt/homebrew/lib"]


def test_config_parser():
    data = """
    [options]
    includes = []
    include_numpy = false
    include_pyarrow = false

    include_somelib = { pkg = "somelib", include = "gets_include", libraries = "gets_libraries", library_dirs = "gets_library_dirs", required_call = "some_setup_op" }

    compile_args = [
        { platforms = ["windows"], arg = "-std=c++17" },
        { platforms = ["linux", "darwin"], arg = "-I/abc/def" },
        { platforms = ["linux", "darwin"], arg = "-Wcpp" },
        { platforms = ["darwin"], arg = "-L/usr/local/opt/llvm/include" },
        { arch = ["anon"], arg = "-O1" },
        { arch = ["x86_64"], arg = "-O2" },
        { arch = ["arm64"], arg = "-O3" },
        { arg = "-py39", marker = "python_version == '3.9'" },
    ]
    extra_link_args =  [
        { platforms = ["darwin"],  arg = "-L/usr/local/opt/llvm/lib" },
        { platforms = ["windows"],  arg = "-LC://abc/def" },
        { platforms = ["linux"], arg = "-L/etc/ssl/ssl.h" },
        { arch = ["arm64"], arg = "-L/usr/include/cpu/simd.h" },
    ]

    define_macros = [
        ["NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"],
        ["ABC_DEF"],
        ["GHI_JKL"],
    ]
    directives = { boundscheck = false, nonecheck = false, language_level = 3, binding = true }

    abc_compile_kwarg = "test"
    """  # noqa: E501

    def gets_include():
        return "abc"

    def gets_libraries():
        return ["lib-a"]

    def gets_library_dirs():
        return ["dir-a"]

    ran = False

    def some_setup_op():
        nonlocal ran
        ran = True

    with pyversion():
        with import_module(
            gets_include=gets_include,
            gets_libraries=gets_libraries,
            gets_library_dirs=gets_library_dirs,
            some_setup_op=some_setup_op,
        ):

            def getcfg():
                parsed = loads(dedent(data))
                return parse_from_dict(SimpleNamespace(config=parsed))

            cfg = getcfg()
            assert ran
            assert len(getcfg().compile_args)

            with pyversion("3", "9"), arch_platform("arm64", "darwin"), patch_path("arm64"):
                cfg = getcfg()
                assert sorted(cfg.compile_args_for_platform) == sorted(
                    [
                        "-I/abc/def",
                        "-py39",
                        "-Wcpp",
                        "-I/opt/homebrew/include",
                        "-O3",
                        "-L/usr/local/opt/llvm/include",
                    ]
                )

            with arch_platform("x86_64", "windows"):
                cfg = getcfg()
                assert sorted(cfg.compile_args_for_platform) == sorted(
                    [
                        "-std=c++17",
                        "-O2",
                    ]
                )
                assert sorted(cfg.compile_links_for_platform) == sorted(["-LC://abc/def"])
            with arch_platform("x86_64", "linux"), patch_path("x86_64", "/usr/local/opt"):
                cfg = getcfg()
                assert sorted(cfg.compile_args_for_platform) == sorted(
                    [
                        "-I/usr/local/include",
                        "-I/abc/def",
                        "-Wcpp",
                        "-O2",
                    ]
                )
                assert sorted(cfg.compile_links_for_platform) == sorted(
                    ["-L/usr/local/lib", "-L/usr/local/opt", "-L/etc/ssl/ssl.h"]
                )
            with arch_platform("x86_64", "darwin"), patch_path("x86_64"):
                cfg = getcfg()
                assert sorted(cfg.compile_args_for_platform) == sorted(
                    [
                        "-I/usr/local/include",
                        "-I/abc/def",
                        "-Wcpp",
                        "-L/usr/local/opt/llvm/include",
                        "-O2",
                    ]
                )
                assert sorted(cfg.compile_links_for_platform) == sorted(
                    [
                        "-L/usr/local/lib",
                        "-L/usr/local/opt",
                        "-L/usr/local/opt/llvm/lib",
                    ]
                )

            with arch_platform("arm64", "windows"):
                cfg = getcfg()

                assert sorted(cfg.compile_args_for_platform) == sorted(
                    [
                        "-std=c++17",
                        "-O3",
                    ]
                )
                assert sorted(cfg.compile_links_for_platform) == sorted(["-LC://abc/def", "-L/usr/include/cpu/simd.h"])
            with arch_platform("arm64", "linux"), patch_path("x86_64"):
                cfg = getcfg()

                assert sorted(cfg.compile_args_for_platform) == sorted(
                    [
                        "-I/usr/local/include",
                        "-I/abc/def",
                        "-Wcpp",
                        "-O3",
                    ]
                )
                assert sorted(cfg.compile_links_for_platform) == sorted(
                    [
                        "-L/usr/local/lib",
                        "-L/usr/local/opt",
                        "-L/etc/ssl/ssl.h",
                        "-L/usr/include/cpu/simd.h",
                    ]
                )
            with arch_platform("arm64", "darwin"), patch_path("arm64"):
                cfg = getcfg()
                assert sorted(cfg.compile_args_for_platform) == sorted(
                    [
                        "-I/opt/homebrew/include",
                        "-I/abc/def",
                        "-Wcpp",
                        "-L/usr/local/opt/llvm/include",
                        "-O3",
                    ]
                )
                assert sorted(cfg.compile_links_for_platform) == sorted(
                    [
                        "-L/opt/homebrew/lib",
                        "-L/usr/local/opt/llvm/lib",
                        "-L/usr/include/cpu/simd.h",
                    ]
                )

            with arch_platform("", "windows"):
                cfg = getcfg()

                assert sorted(cfg.compile_args_for_platform) == sorted(["-std=c++17", "-O1"])
                assert sorted(cfg.compile_links_for_platform) == sorted(
                    [
                        "-LC://abc/def",
                    ]
                )
            with arch_platform("", "linux"), patch_path("x86_64"):
                cfg = getcfg()

                assert sorted(cfg.compile_args_for_platform) == sorted(
                    ["-I/usr/local/include", "-I/abc/def", "-Wcpp", "-O1"]
                )
                assert sorted(cfg.compile_links_for_platform) == sorted(
                    [
                        "-L/usr/local/lib",
                        "-L/usr/local/opt",
                        "-L/etc/ssl/ssl.h",
                    ]
                )
            with arch_platform("", "darwin"), patch_path("x86_64"):
                cfg = getcfg()
                assert sorted(cfg.compile_args_for_platform) == sorted(
                    [
                        "-I/usr/local/include",
                        "-I/abc/def",
                        "-Wcpp",
                        "-L/usr/local/opt/llvm/include",
                        "-O1",
                    ]
                )
                assert sorted(cfg.compile_links_for_platform) == sorted(
                    [
                        "-L/usr/local/lib",
                        "-L/usr/local/opt",
                        "-L/usr/local/opt/llvm/lib",
                    ]
                )

            cfg = getcfg()

    assert cfg.directives == {"boundscheck": False, "nonecheck": False, "language_level": 3, "binding": True}
    assert cfg.libraries == gets_libraries()
    assert cfg.library_dirs == gets_library_dirs()
    assert gets_include() in cfg.includes
    assert cfg.compile_kwargs == {"abc_compile_kwarg": "test"}


def test_defaults():
    data = """
    [options]
    """
    parsed = loads(dedent(data))

    def getcfg():
        return parse_from_dict(SimpleNamespace(config=parsed))

    cfg = getcfg()
    assert cfg.directives == {"language_level": 3, "binding": True}

    with arch_platform("x86_64", "windows"):
        cfg = getcfg()

        assert sorted(cfg.compile_args_for_platform) == sorted(
            [
                "-O2",
            ]
        )
        assert sorted(cfg.compile_links_for_platform) == sorted([])
    with arch_platform("x86_64", "linux"), patch_path("x86_64"):
        cfg = getcfg()
        assert sorted(cfg.compile_args_for_platform) == sorted(["-I/usr/local/include", "-O2"])
        assert sorted(cfg.compile_links_for_platform) == sorted(["-L/usr/local/opt", "-L/usr/local/lib"])
    with arch_platform("x86_64", "darwin"), patch_path("x86_64"):
        cfg = getcfg()
        assert sorted(cfg.compile_args_for_platform) == sorted(
            [
                "-O2",
                "-I/usr/local/include",
            ]
        )
        assert sorted(cfg.compile_links_for_platform) == sorted(["-L/usr/local/opt", "-L/usr/local/lib"])

    with arch_platform("arm64", "windows"):
        cfg = getcfg()

        assert sorted(cfg.compile_args_for_platform) == sorted(
            [
                "-O2",
            ]
        )
        assert sorted(cfg.compile_links_for_platform) == sorted([])
    with arch_platform("arm64", "linux"), patch_path("x86_64"):
        cfg = getcfg()

        assert sorted(cfg.compile_args_for_platform) == sorted(
            [
                "-I/usr/local/include",
                "-O2",
            ]
        )
        assert sorted(cfg.compile_links_for_platform) == sorted(["-L/usr/local/lib", "-L/usr/local/opt"])
    with arch_platform("arm64", "darwin"), patch_path("arm64"):
        cfg = getcfg()

        assert sorted(cfg.compile_args_for_platform) == sorted(
            [
                "-I/opt/homebrew/include",
                "-O2",
            ]
        )
        assert sorted(cfg.compile_links_for_platform) == sorted(
            [
                "-L/opt/homebrew/lib",
            ]
        )

    with arch_platform("", "windows"):
        cfg = getcfg()

        assert sorted(cfg.compile_args_for_platform) == sorted(["-O2"])
        assert sorted(cfg.compile_links_for_platform) == sorted([])

    with arch_platform("", "linux"), patch_path("x86_64", "/etc/ssl/ssl.h"):
        cfg = getcfg()

        assert sorted(cfg.compile_args_for_platform) == sorted(
            [
                "-O2",
                "-I/usr/local/include",
            ]
        )
        assert sorted(cfg.compile_links_for_platform) == sorted(
            [
                "-L/usr/local/opt",
                "-L/usr/local/lib",
            ]
        )

    with arch_platform("", "darwin"), patch_path("x86_64"):
        cfg = getcfg()
        assert sorted(cfg.compile_args_for_platform) == sorted(
            [
                "-O2",
                "-I/usr/local/include",
            ]
        )
        assert sorted(cfg.compile_links_for_platform) == sorted(
            [
                "-L/usr/local/opt",
                "-L/usr/local/lib",
            ]
        )

    cfg = getcfg()
    assert cfg.compile_kwargs == {}
