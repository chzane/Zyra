from pathlib import Path
import json
from pydantic import BaseModel, ConfigDict


class ZyraBaseData(BaseModel):
    """
    Base class for Zyra configuration.
    """
    
    model_config = ConfigDict(extra="ignore")

    def get(self, path: str, default=None):
        """
        Get a configuration value by path.
        
        Args:
            path (str): The path to the configuration value.
            default (any, optional): The default value to return if the path is not found.
            
        Returns:
            any: The configuration value or the default value if not found.
        """
        obj = self

        for key in path.split("."):
            if not hasattr(obj, key):
                return default
            obj = getattr(obj, key)

        return obj

    def set(self, path: str, value):
        """
        Set a configuration value by path.
        
        Args:
            path (str): The path to the configuration value.
            value (any): The value to set.
        """
        parts = path.split(".")
        obj = self

        for key in parts[:-1]:
            obj = getattr(obj, key)

        setattr(obj, parts[-1], value)

    def update_from_dict(self, data: dict):
        """
        Update the configuration with data from a dictionary.
        
        Args:
            data (dict): The dictionary containing configuration data.
        """
        for key, value in data.items():
            current = getattr(self, key, None)

            if isinstance(current, ZyraBaseData) and isinstance(value, dict):
                current.update_from_dict(value)
            else:
                setattr(self, key, value)

    def to_dict(self):
        return self.model_dump()

    def save(self, path: str | Path):
        """
        Save the configuration to a file.
        
        Args:
            path (str | Path): The path to the configuration file.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            json.dumps(self.model_dump(mode="json"), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def load_or_create(self, path: str | Path):
        """
        Load config from file, merge missing fields with defaults,
        and create the file if it does not exist.
        
        Args:
            path (str | Path): The path to the configuration file.
            
        Returns:
            ZyraBaseData: The loaded or created data object.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if not path.exists():
            self.save(path)
            return self

        try:
            raw_data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            raw_data = {}

        default_data = self.model_dump(mode="python")

        def merge(defaults: dict, current: dict):
            result = defaults.copy()

            for key, value in current.items():
                if key not in result:
                    continue
                if (
                    isinstance(result[key], dict)
                    and isinstance(value, dict)
                ):
                    result[key] = merge(result[key], value)
                else:
                    result[key] = value

            return result

        merged = merge(default_data, raw_data)

        updated = self.__class__.model_validate(merged)

        for key, value in updated.__dict__.items():
            setattr(self, key, value)

        self.save(path)

        return self


class ZyraBaseConfig(ZyraBaseData):
    pass


class ZyraBaseState(ZyraBaseData):
    pass
