import re
from dataclasses import asdict, dataclass, field
from textwrap import dedent

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from hatch_cython.config.platform import PlatformBase
from hatch_cython.constants import NORM_GLOB
from hatch_cython.types import ListStr, ListT, UnionT
from hatch_cython.utils import parse_user_glob


def idx_search_mod(s: str):
    if not s.startswith("*"):
        s = "*" + s
    # replace the ./ because we do so to the file
    return s.replace("./", "")


@dataclass
class IndexItem(PlatformBase):
    keyword: str = "*"
    matches: UnionT[str, ListStr] = field(default_factory=list)

    def __post_init__(self):
        matches = self.matches
        if isinstance(matches, str):
            matches = [matches]
        for i in range(len(matches)):
            matches[i] = parse_user_glob(matches[i], r"([^.]*)", idx_search_mod)
        self.matches = sorted(matches, key=lambda it: -1 if it == NORM_GLOB else 1)

    def file_match(self, file: str) -> bool:
        for patt in self.matches:
            # we take the local part out since we match on extensions
            if re.match(patt, file.replace("./", "")):
                return True
        return False


class Templates:
    index: ListT[IndexItem]
    kwargs: dict

    def __init__(self, index: ListT[IndexItem] = None, **kwargs):
        if index is None:
            index = []

        # reverse everything & put global first so that it is always overriden.
        # FIFO priority after that
        self.index = sorted(index[::-1], key=lambda it: -1 if it.keyword == "global" else 1)  # noqa: C415
        for kw, arg in kwargs.items():
            if not isinstance(arg, dict):
                msg = (
                    f"'{kw} = {arg}' ({type(arg)}) is invalid. "
                    "keyword arguments must be defined as "
                    "'keyword = { abc = 1, ... }' in your "
                    "pyproject.toml / hatch.toml"
                )
                raise ValueError(msg, arg)
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return dedent(
            f"""Templates(
    index={self.index},
    kwargs={self.kwargs}
)"""
        )

    def asdict(self):
        return {
            "index": [asdict(i) for i in self.index],
            "kwargs": self.kwargs,
        }

    def find(self, cls: BuildHookInterface, *files: str):
        kwds = {}

        for can in self.index:
            for file in files:
                if can.file_match(file) and can.applies():
                    add = self.kwargs.get(can.keyword)
                    if add is None:
                        msg = (
                            f"'{can.keyword}' is defined but returns no "
                            "kwargs. To define kwargs, put "
                            f"'{can.keyword} = {{ abc = 1, ... }}' in your"
                            "pyproject.toml / hatch.toml"
                        )
                        cls.app.display_warning(msg)
                    else:
                        kwds = {**kwds, **add}
        # raise ValueError(kwds, files, self.index)
        return kwds


def parse_template_kwds(clsvars: dict):
    try:
        idx = clsvars.pop("index")
    except KeyError:
        idx = []
    idx = [IndexItem(**kw) for kw in idx]
    return Templates(index=idx, **clsvars)
