import re
from dataclasses import dataclass, field
from typing import Type

from hatch_cython.config.platform import PlatformBase
from hatch_cython.types import DictT, ListT, UnionT
from hatch_cython.utils import parse_user_glob


@dataclass
class OptExclude(PlatformBase):
    matches: str = field(default="*")


@dataclass
class OptInclude(PlatformBase):
    matches: str = field(default="*")


def _get_file_list(
        cls: Type[UnionT[OptInclude, OptExclude]],
        files: ListT[UnionT[str, OptInclude, OptExclude]]
) -> ListT[str]:
    return [
        *[cls(**d) for d in files if isinstance(d, dict)],
        *[cls(matches=s) for s in files if isinstance(s, str)],
    ]


@dataclass
class FileArgs:
    targets: ListT[UnionT[str, OptInclude]] = field(default_factory=list)
    exclude: ListT[UnionT[str, OptExclude]] = field(default_factory=list)
    aliases: DictT[str, str] = field(default_factory=dict)
    exclude_compiled_src: ListT[UnionT[str, OptExclude]] = field(default_factory=list)
    include_compiled_src: ListT[UnionT[str, OptInclude]] = field(default_factory=list)

    def __post_init__(self):
        rep = {}
        for k, v in self.aliases.items():
            rep[parse_user_glob(k)] = v
        self.aliases = rep
        self.exclude = _get_file_list(OptExclude, self.exclude)
        self.targets = _get_file_list(OptInclude, self.targets)
        self.exclude_compiled_src = _get_file_list(OptExclude, self.exclude_compiled_src)
        self.include_compiled_src = _get_file_list(OptInclude, self.include_compiled_src)

    @property
    def explicit_targets(self) -> bool:
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
