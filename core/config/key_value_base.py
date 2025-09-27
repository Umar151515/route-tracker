import json
from pathlib import Path
from typing import Any
from abc import ABC

from jinja2 import Template


class KeyValueBase(ABC):
    _instance = {}
    _keys: list[str]
    config_path: Path
    
    _default_config = """{
    {%- for key in keys %}
    "{{ key }}": ""{% if not loop.last %},{% endif %}
    {%- endfor %}
}"""

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super().__new__(cls)
        return cls._instance[cls]
    
    def __init__(self):
        if not hasattr(self, 'config'):
            self.config: dict[str, Any] | None = None
            self.load()

    def _ensure_loaded(self):
        if self.config is None:
            raise RuntimeError(f"{self.__class__} not loaded. Call load() first")

    def load(self):
        if not self.config_path.exists():
            with open(self.config_path, 'w', encoding="utf-8") as file:
                file.write(Template(self._default_config).render(keys=self._keys))
            raise FileNotFoundError(
                f"Config file was not found and has been created at: {self.config_path}\n"
                "Please fill in the required configuration before the next run."
            )
        with open(self.config_path, "r", encoding="utf-8") as config_file:
            self.config = json.load(config_file)

    def has(self, key: str) -> bool:
        self._ensure_loaded()
        return key in self.config

    def get(self, key: str, default:str|None = None) -> Any:
        self._ensure_loaded()
        value = self.config.get(key, default)
        if value is None:
            raise ValueError(f"{self.__class__} '{key}' not set and no default provided")
        return value
    
    def set(self, key: str, value: Any) -> None:
        self._ensure_loaded()
        self.config[key] = value
        with open(self.config_path, "w", encoding="utf-8") as config_file:
            json.dump(self.config, config_file, ensure_ascii=False, indent=4)
    
    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        self.set(key, value)