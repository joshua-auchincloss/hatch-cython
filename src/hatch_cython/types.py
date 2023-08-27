from sys import version_info
from typing import TypeVar, Union

T = TypeVar("T")

vmaj = (version_info[0], version_info[1])
if vmaj >= (3, 10):
    from typing import ParamSpec

    list_t = list
    ListStr = list[str]
else:
    from typing import List  # noqa: UP035

    from typing_extensions import ParamSpec

    list_t = List  # noqa: UP006
    ListStr = List[str]  # noqa: UP006

P = ParamSpec("P")
union_t = Union
