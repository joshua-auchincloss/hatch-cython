from dataclasses import dataclass, field

from hatch_cython.types import ListStr


@dataclass
class FileArgs:
    exclude: ListStr = field(default_factory=list)
