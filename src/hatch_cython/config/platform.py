from collections.abc import Hashable
from dataclasses import dataclass
from os import path

from packaging.markers import Marker

from hatch_cython.constants import ANON
from hatch_cython.types import CallableT, ListStr, ListT, UnionT
from hatch_cython.utils import aarch, plat


@dataclass
class PlatformBase(Hashable):
    platforms: UnionT[ListStr, str] = "*"
    arch: UnionT[ListStr, str] = "*"
    depends_path: bool = False
    marker: str = None
    apply_to_marker: CallableT[[], bool] = None

    def __post_init__(self):
        self.do_rewrite("platforms")
        self.do_rewrite("arch")

    def do_rewrite(self, attr: str):
        att = getattr(self, attr)
        if isinstance(att, list):
            setattr(self, attr, [p.lower() for p in att])
        elif isinstance(att, str):
            setattr(self, attr, att.lower())

    def check_marker(self):
        do = True
        if self.apply_to_marker:
            do = self.apply_to_marker()
        if do:
            marker = Marker(self.marker)
            return marker.evaluate()
        return False

    def _applies_impl(self, attr: str, defn: str):
        if self.marker:
            ok = self.check_marker()
            if not ok:
                return False

        att = getattr(self, attr)
        if isinstance(att, list):
            # https://docs.python.org/3/library/platform.html#platform.machine
            # "" is a possible value so we have to add conditions for anon
            _anon = ANON in att and defn == ""
            return defn in att or "*" in att or _anon
        _anon = ANON == att and defn == ""
        return (att in (defn, "*")) or _anon

    def applies(self, platform: UnionT[None, str] = None, arch: UnionT[None, str] = None):
        if platform is None:
            platform = plat()
        if arch is None:
            arch = aarch()

        _isplatform = self._applies_impl("platforms", platform)
        _isarch = self._applies_impl("arch", arch)
        return _isplatform and _isarch

    def is_exist(self, trim: int = 0):
        if self.depends_path:
            return path.exists(self.arg[trim:])
        return True


@dataclass
class PlatformArgs(PlatformBase):
    arg: str = None

    def __hash__(self) -> int:
        return hash(self.arg)


def parse_to_plat(cls, arg, args: UnionT[list, dict], key: UnionT[int, str], require_argform: bool, **kwargs):
    if isinstance(arg, dict):
        args[key] = cls(**arg, **kwargs)
    elif require_argform:
        msg = f"arg {key} is invalid. must be of type ({{ flag = ... , platform = '*' }}) given {arg} ({type(arg)})"
        raise ValueError(msg)


def parse_platform_args(
    kwargs: dict,
    name: str,
    default: CallableT[[], ListT[PlatformArgs]],
) -> ListT[UnionT[str, PlatformArgs]]:
    try:
        args = [*default(), *kwargs.pop(name)]
        for i, arg in enumerate(args):
            parse_to_plat(PlatformArgs, arg, args, i, require_argform=False)
    except KeyError:
        args = default()
    return args


ListedArgs = ListT[UnionT[PlatformArgs, str]]
"""
List[str | PlatformArgs]
"""
