from pathlib import Path

from pydantic import Field
from config.base_config import ZyraBaseState
from .items.auth_state import AuthState
from .items.system_state import SystemState


class ZyraState(ZyraBaseState):
    auth: AuthState = AuthState()
    system: SystemState = SystemState()
    state_dir: Path | None = Field(default=None, exclude=True)
