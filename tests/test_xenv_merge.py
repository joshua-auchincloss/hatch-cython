from textwrap import dedent
from types import SimpleNamespace

import toml

from hatch_cython.config import parse_from_dict

from .utils import arch_platform, override_env


def test_xenvvars():
    data = """
    [options]
    env = [
        { env = "CC", arg = "c++" },
        { env = "CPP", arg = "c++" },
        { env = "CXX", arg = "c++" },
        { env = "CFLAGS", arg = "flag2" },
        { env = "CPPFLAGS", arg = "flag2" },
        { env = "LDFLAGS", arg = "flag2" },
        { env = "CUSTOM_1", arg = "flag2",  arch = "x86_64" },
        { env = "CUSTOM_2", arg = "flag2",  merges = true },
    ]
    """

    def getcfg():
        parsed = toml.loads(dedent(data))
        return parse_from_dict(SimpleNamespace(config=parsed))

    f1 = "flag1"
    f2 = "flag2"
    with override_env({"CFLAGS": f1, "CPPFLAGS": f1, "LDFLAGS": f1}):
        cfg = getcfg()

        f12 = "flag1 flag2"
        assert cfg.envflags.CC.arg == "c++"
        assert cfg.envflags.LDFLAGS.arg == "flag2"

        assert cfg.envflags.env.get("CC") == "c++"
        assert cfg.envflags.env.get("CFLAGS") == f12
        assert cfg.envflags.env.get("CPPFLAGS") == f12
        assert cfg.envflags.env.get("LDFLAGS") == f12

        with override_env({"CUSTOM_1": f1}):
            with arch_platform("x86_64", ""):
                cfg = getcfg()
                assert cfg.envflags.env.get("CUSTOM_1") == f2
            with arch_platform("", ""):
                cfg = getcfg()
                assert cfg.envflags.env.get("CUSTOM_1") == f1

        with override_env({"CUSTOM_2": f1}):
            cfg = getcfg()
            assert cfg.envflags.env.get("CUSTOM_2") == f12
