from typing import TypeVar

from numpy import longlong
from numpy.typing import NDArray

T = TypeVar("T")

def hello_world(name: str): ...
def hello_numpy(arr: NDArray[longlong]): ...
