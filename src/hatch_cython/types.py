from sys import version_info
from typing import TypeVar

A = TypeVar("A")
"""Union A"""
B = TypeVar("B")
"""Union B"""
T = TypeVar("T")
"""Generic T"""
Un = TypeVar("Un")
"""Union Output"""

vmaj = (version_info[0], version_info[1])
if vmaj >= (3, 10):
    ListStr = list[str]
else:
    from typing import List, Union  # noqa: UP035

    ListStr = List[str]  # noqa: UP006


def union_t(a: A, b: B) -> Un:
    if vmaj >= (3, 10):
        return a | b
    else:
        return Union[a, b]  # noqa: UP007


def list_t(of: A) -> B:
    if vmaj >= (3, 9):
        return list[of]
    return List[of]  # noqa: UP006
