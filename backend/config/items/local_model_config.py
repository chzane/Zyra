from pathlib import Path
from ..base_config import ZyraBaseConfig


class LocalModelConfig(ZyraBaseConfig):
    enabled: bool = True
    model_dir: Path | None = None
    unload_after_seconds: int = 300