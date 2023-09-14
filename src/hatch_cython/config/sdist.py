from dataclasses import dataclass

from hatch_cython.config.platform import PlatformBase
from hatch_cython.types import ListT


@dataclass
class SdistConfig:
    platforms: ListT[PlatformBase]


def parse_sdist(kws: dict):
    pfs = kws.pop("platforms", [])
    return SdistConfig(**kws, platforms=pfs)
