import os
from dotenv import load_dotenv
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings

from .items.app_config import AppConfig
from .items.llm_config import LLMConfig
from .items.server_config import ServerConfig

from .base_config import ZyraBaseConfig

class ZyraConfig(ZyraBaseConfig, BaseSettings):
    app: AppConfig = AppConfig()
    llm: LLMConfig = LLMConfig()
    server: ServerConfig = ServerConfig()
    
    _env_file: Path | None = None
    config_dir: Path | None = Field(default=None, exclude=True)

    def load_env(self, env_file: str | Path = ".env", override: bool = True):
        """
        Load values from a .env file into process environment.

        Example:
            config.load_env()
            config.load_env("config/dev.env")
        """

        env_path = Path(env_file).expanduser().resolve()

        if not env_path.exists():
            raise FileNotFoundError(f".env file not found: {env_path}")

        load_dotenv(env_path, override=override)
        self._env_file = env_path

    def get_env(
        self,
        key: str,
        default: str | None = None,
        cast: type | None = None
    ):
        """
        Read a value from environment variables.

        Example:
            config.get_env("ZYRA_API_KEY")
            config.get_env("SERVER_PORT", cast=int)
            config.get_env("DEBUG", cast=bool)
        """

        value = os.getenv(key, default)

        if value is None or cast is None:
            return value

        try:
            if cast is bool:
                return str(value).strip().lower() in {
                    "1", "true", "yes", "on"
                }

            return cast(value)

        except Exception as exc:
            raise ValueError(
                f"Failed to cast env variable {key!r} to {cast.__name__}: {value!r}"
            ) from exc

    def require_env(
        self,
        key: str,
        cast: type | None = None
    ):
        """
        Same as get_env, but raises if the variable does not exist.
        A tiny iron key for doors that absolutely must open 🔑
        """

        value = self.get_env(key, cast=cast)

        if value is None:
            source = f" in {self._env_file}" if self._env_file else ""
            raise ValueError(
                f"Required environment variable not found: {key}{source}"
            )

        return value
