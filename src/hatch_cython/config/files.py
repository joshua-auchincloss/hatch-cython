import re
from dataclasses import dataclass, field

from hatch_cython.types import ListStr, UnionT, dict_t
from hatch_cython.utils import parse_user_glob


@dataclass
class FileArgs:
    exclude: ListStr = field(default_factory=list)
    aliases: dict_t[str, str] = field(default_factory=dict)

    def __post_init__(self):
        rep = {}
        for k, v in self.aliases.items():
            rep[parse_user_glob(k)] = v
        self.aliases = rep

    def matches_alias(self, other: str) -> UnionT[str, None]:
        matched = [re.match(v, other) for v in self.aliases.keys()]
        if any(matched):
            first = 0
            for ok in matched:
                if ok:
                    break
                first += 1
            return self.aliases[list(self.aliases.keys())[first]]
