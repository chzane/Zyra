from pathlib import Path
from threading import RLock
from functools import lru_cache
from . import ZyraConfig

_CONFIG_LOCK = RLock()


@lru_cache
def get_config() -> ZyraConfig:
    return ZyraConfig()


def get_app_config() -> ZyraConfig:
    return get_config()


def get_config_file_path() -> Path:
    config = get_config()
    if config.config_dir is None:
        raise ValueError("config.config_dir is not set")
    return Path(config.config_dir) / "config.json"


def save_config() -> Path:
    config = get_config()
    config_file = get_config_file_path()
    with _CONFIG_LOCK:
        config.save(config_file)
    return config_file
