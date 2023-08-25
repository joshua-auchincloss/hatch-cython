from sys import version_info
from typing import TypeVar

A = TypeVar("A")
B = TypeVar("B")
Un = TypeVar("Un")

vmaj = (version_info[0], version_info[1])
if vmaj >= (3, 10):
    ListStr = list[str]
else:
    from typing import List, Union  # noqa: UP035

    ListStr = List[str]  # noqa: UP006


def union_t(a: A, b: B) -> Un:
    if vmaj >= (3, 10):
        union: Un = a | b
    else:
        union: Un = Union[a, b]  # noqa: UP007
    return union


def list_t(of: A) -> B:
    if vmaj >= (3, 9):
        return list[of]
    return List[of]  # noqa: UP006
