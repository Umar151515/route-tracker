from ..config import (
    EnvManager,
    AppConfig,
    LoggingManager
)


class ConfigManager:
    env: EnvManager = EnvManager()
    app: AppConfig = AppConfig()
    log: LoggingManager = LoggingManager()

    @classmethod
    def reload_all(cls):
        cls.env = EnvManager()
        cls.app = AppConfig()
        cls.log = LoggingManager()