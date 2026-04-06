from ..base_config import ZyraBaseConfig


class AppConfig(ZyraBaseConfig):
    name: str = "Zyra"
    version: str = "1.0.0beta"
    is_dev: bool = False
    