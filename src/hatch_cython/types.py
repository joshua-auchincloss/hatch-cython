from sys import version_info
from typing import Literal, TypeVar, Union

T = TypeVar("T")

vmaj = (version_info[0], version_info[1])
if vmaj >= (3, 10):
    from collections.abc import Callable
    from typing import ParamSpec

    dict_t = dict
    list_t = list
    ListStr = list[str]
else:
    from typing import Callable, Dict, List  # noqa: UP035

    from typing_extensions import ParamSpec

    dict_t = Dict  # noqa: UP006
    list_t = List  # noqa: UP006

P = ParamSpec("P")
ListStr = list_t[str]
UnionT = Union
CorePlatforms = Literal[
    "darwin",
    "linux",
    "windows",
]

CallableT = Callable
