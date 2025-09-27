from ..config import (
    EnvManager,
    AppConfig
)


class ConfigManager:
    env: EnvManager = EnvManager()
    app: AppConfig = AppConfig()

    @classmethod
    def reload_all(cls):
        cls.env = EnvManager()
        cls.app = AppConfig()