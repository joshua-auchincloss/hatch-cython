from typing import Generic, Protocol, TypeVar

from numpy import longlong

T = TypeVar("T")

class NDArray(Generic[T], Protocol): ...

def hello_world(name: str): ...
def hello_numpy(arr: NDArray[longlong]): ...
