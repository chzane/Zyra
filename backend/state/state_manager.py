from functools import lru_cache
from . import ZyraState


@lru_cache
def get_state() -> ZyraState:
    return ZyraState()
