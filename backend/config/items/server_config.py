from ..base_config import ZyraBaseConfig


class ServerConfig(ZyraBaseConfig):
    host: str = "127.0.0.1"
    port: int = 8888
