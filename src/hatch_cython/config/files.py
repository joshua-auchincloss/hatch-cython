import re
from dataclasses import dataclass, field

from hatch_cython.config.platform import PlatformBase
from hatch_cython.types import DictT, ListT, UnionT
from hatch_cython.utils import parse_user_glob


@dataclass
class OptExclude(PlatformBase):
    matches: str = field(default="*")


@dataclass
class OptInclude(PlatformBase):
    matches: str = field(default="*")


@dataclass
class FileArgs:
    targets: ListT[UnionT[str, OptInclude]] = field(default_factory=list)
    exclude: ListT[UnionT[str, OptExclude]] = field(default_factory=list)
    aliases: DictT[str, str] = field(default_factory=dict)

    def __post_init__(self):
        rep = {}
        for k, v in self.aliases.items():
            rep[parse_user_glob(k)] = v
        self.aliases = rep
        self.exclude = [
            *[OptExclude(**d) for d in self.exclude if isinstance(d, dict)],
            *[OptExclude(matches=s) for s in self.exclude if isinstance(s, str)],
        ]
        self.targets = [
            *[OptInclude(**d) for d in self.targets if isinstance(d, dict)],
            *[OptInclude(matches=s) for s in self.targets if isinstance(s, str)],
        ]

    @property
    def explicit_targets(self):
        return len(self.targets) > 0

    def matches_alias(self, other: str) -> UnionT[str, None]:
        matched = [re.match(v, other) for v in self.aliases.keys()]
        if any(matched):
            first = 0
            for ok in matched:
                if ok:
                    break
                first += 1
            return self.aliases[list(self.aliases.keys())[first]]
