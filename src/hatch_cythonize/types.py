from sys import version_info
from typing import Literal, TypeVar, Union

T = TypeVar("T")

vmaj = (version_info[0], version_info[1])
if vmaj >= (3, 10):
    from collections.abc import Callable
    from typing import ParamSpec

    TupleT = tuple
    DictT = dict
    ListT = list
    Set = set
else:
    from typing import Callable, Dict, List, Set, Tuple  # noqa: UP035, F401

    from typing_extensions import ParamSpec

    TupleT = Tuple  # noqa: UP006
    DictT = Dict  # noqa: UP006
    ListT = List  # noqa: UP006

P = ParamSpec("P")
ListStr = ListT[str]
UnionT = Union
CorePlatforms = Literal[
    "darwin",
    "linux",
    "windows",
]
CallableT = Callable
