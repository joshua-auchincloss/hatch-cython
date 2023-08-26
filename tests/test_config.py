from textwrap import dedent
from types import SimpleNamespace
from unittest.mock import patch

from toml import loads

from hatch_cython.config import parse_from_dict

from .utils import arch_platform, true_if_eq

true_x86_mac = true_if_eq("/usr/local/include", "/usr/local/lib")
true_arm_mac = true_if_eq("/opt/homebrew/lib", "/opt/homebrew/include")


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
    ]
    extra_link_args =  [
    { platforms = ["darwin"],  arg = "-L/usr/local/opt/llvm/lib" },
    { platforms = ["windows"],  arg = "-LC://abc/def" },
    { platforms = ["linux"], arg = "-L/etc/ssl/ssl.h" },
    { arch = ["arm64"], arg = "-L/usr/include/cpu/simd.h" },
    ]

    directives = { boundscheck = false, nonecheck = false, language_level = 3, binding = true }

    language = "c++"
    abc_compile_kwarg = "test"
    """  # noqa: E501
    parsed = loads(dedent(data))

    def get_include():
        return "abc"

    def gets_libraries():
        return ["lib-a"]

    def gets_library_dirs():
        return ["dir-a"]

    ran = False

    def some_setup_op():
        nonlocal ran
        ran = True

    with patch(
        "hatch_cython.config.import_module",
        (
            lambda _: SimpleNamespace(
                gets_include=get_include,
                gets_libraries=gets_libraries,
                gets_library_dirs=gets_library_dirs,
                some_setup_op=some_setup_op,
            )
        ),
    ):
        def getcfg():
            return parse_from_dict(SimpleNamespace(config=parsed))
        cfg = getcfg()
        assert ran

        assert getcfg().compile_args

        with arch_platform("x86_64", "windows"):
            cfg = getcfg()
            assert cfg.compile_args_for_platform == [
                "-std=c++17",
                "-O2",
                "-arch x86_64",
            ]
            assert cfg.compile_links_for_platform == ["-LC://abc/def"]
        with arch_platform("x86_64", "linux"):
            cfg = getcfg()
            assert cfg.compile_args_for_platform == [
                "-I/abc/def",
                "-Wcpp",
                "-O2",
                "-arch x86_64",
            ]
            assert cfg.compile_links_for_platform == ["-L/etc/ssl/ssl.h"]
        with arch_platform("x86_64", "darwin"):
            cfg = getcfg()

            with patch("hatch_cython.config.path.exists", true_x86_mac):
                assert cfg.compile_args_for_platform == [
                    "-I/usr/local/include",
                    "-I/abc/def",
                    "-Wcpp",
                    "-L/usr/local/opt/llvm/include",
                    "-O2",
                    "-arch x86_64",
                ]
                assert cfg.compile_links_for_platform == ["-L/usr/local/lib", "-L/usr/local/opt/llvm/lib"]

        with arch_platform("arm64", "windows"):
            cfg = getcfg()

            assert cfg.compile_args_for_platform == [
                "-std=c++17",
                "-O3",
                "-arch arm64",
            ]
            assert cfg.compile_links_for_platform == ["-LC://abc/def", "-L/usr/include/cpu/simd.h"]
        with arch_platform("arm64", "linux"):
            cfg = getcfg()

            assert cfg.compile_args_for_platform == [
                "-I/abc/def",
                "-Wcpp",
                "-O3",
                "-arch arm64",
            ]
            assert cfg.compile_links_for_platform == ["-L/etc/ssl/ssl.h", "-L/usr/include/cpu/simd.h"]
        with arch_platform("arm64", "darwin"):
            cfg = getcfg()

            with patch("hatch_cython.config.path.exists", true_arm_mac):
                assert cfg.compile_args_for_platform == [
                    "-I/opt/homebrew/include",
                    "-I/abc/def",
                    "-Wcpp",
                    "-L/usr/local/opt/llvm/include",
                    "-O3",
                    "-arch arm64",
                ]
                assert cfg.compile_links_for_platform == [
                    "-L/opt/homebrew/lib",
                    "-L/usr/local/opt/llvm/lib",
                    "-L/usr/include/cpu/simd.h",
                ]

        with arch_platform("", "windows"):
            cfg = getcfg()

            assert cfg.compile_args_for_platform == ["-std=c++17", "-O1"]
            assert cfg.compile_links_for_platform == [
                "-LC://abc/def",
            ]
        with arch_platform("", "linux"):
            cfg = getcfg()

            assert cfg.compile_args_for_platform == ["-I/abc/def", "-Wcpp", "-O1"]
            assert cfg.compile_links_for_platform == [
                "-L/etc/ssl/ssl.h",
            ]
        with arch_platform("", "darwin"):
            cfg = getcfg()

            with patch("hatch_cython.config.path.exists", true_x86_mac):
                assert cfg.compile_args_for_platform == [
                    "-I/usr/local/include",
                    "-I/abc/def",
                    "-Wcpp",
                    "-L/usr/local/opt/llvm/include",
                    "-O1",
                ]
                assert cfg.compile_links_for_platform == ["-L/usr/local/lib", "-L/usr/local/opt/llvm/lib"]

        cfg = getcfg()

    assert cfg.directives == {"boundscheck": False, "nonecheck": False, "language_level": 3, "binding": True}
    assert cfg.libraries == gets_libraries()
    assert cfg.library_dirs == gets_library_dirs()
    assert get_include() in cfg.includes
    assert cfg.language == "c++"
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

        assert cfg.compile_args_for_platform == [
            "-O2",
            "-arch x86_64",
        ]
        assert cfg.compile_links_for_platform == []
    with arch_platform("x86_64", "linux"):
        cfg = getcfg()

        assert cfg.compile_args_for_platform == [
            "-O2",
            "-arch x86_64",
        ]
        assert cfg.compile_links_for_platform == []
    with arch_platform("x86_64", "darwin"):
        cfg = getcfg()

        with patch("hatch_cython.config.path.exists", true_x86_mac):
            assert cfg.compile_args_for_platform == [
                "-I/usr/local/include",
                "-O2",
                "-arch x86_64",
            ]
            assert cfg.compile_links_for_platform == ["-L/usr/local/lib"]

    with arch_platform("arm64", "windows"):
        cfg = getcfg()

        assert cfg.compile_args_for_platform == [
            "-O2",
            "-arch arm64",
        ]
        assert cfg.compile_links_for_platform == []
    with arch_platform("arm64", "linux"):
        cfg = getcfg()

        assert cfg.compile_args_for_platform == [
            "-O2",
            "-arch arm64",
        ]
        assert cfg.compile_links_for_platform == []
    with arch_platform("arm64", "darwin"):
        cfg = getcfg()

        with patch("hatch_cython.config.path.exists", true_arm_mac):
            assert cfg.compile_args_for_platform == [
                "-I/opt/homebrew/include",
                "-O2",
                "-arch arm64",
            ]
            assert cfg.compile_links_for_platform == [
                "-L/opt/homebrew/lib",
            ]

    with arch_platform("", "windows"):
        cfg = getcfg()

        assert cfg.compile_args_for_platform == ["-O2"]
        assert cfg.compile_links_for_platform == []

    with arch_platform("", "linux"):
        cfg = getcfg()

        assert cfg.compile_args_for_platform == ["-O2"]
        assert cfg.compile_links_for_platform == []

    with arch_platform("", "darwin"):
        cfg = getcfg()

        with patch("hatch_cython.config.path.exists", true_x86_mac):
            assert cfg.compile_args_for_platform == [
                "-I/usr/local/include",
                "-O2",
            ]
            assert cfg.compile_links_for_platform == [
                "-L/usr/local/lib",
            ]

    cfg = getcfg()
    assert cfg.language is None
    assert cfg.compile_kwargs == {}
