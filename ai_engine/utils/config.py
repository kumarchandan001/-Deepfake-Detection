import yaml
import os
from typing import Any, Dict

class Config:
    def __init__(self, config_path: str = "ai_engine/configs/config.yaml"):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at: {config_path}")
            
        with open(config_path, "r") as f:
            self._config = yaml.safe_load(f)

    def get(self, path: str, default: Any = None) -> Any:
        keys = path.split(".")
        data = self._config
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
            else:
                return default
        return data if data is not None else default

    @property
    def raw(self) -> Dict[str, Any]:
        return self._config
