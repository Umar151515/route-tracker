import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .paths import app_logging_path


class LoggingManager:
    _instance: "LoggingManager" = None

    MAX_LOG_SIZE = 5 * 1024 * 1024
    BACKUP_COUNT = 3

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_loaded"):
            self._loaded = False
            self.load()

    def load(self):
        log_file = Path(app_logging_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("AppLogger")
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=self.MAX_LOG_SIZE,
                backupCount=self.BACKUP_COUNT,
                encoding="utf-8"
            )
            console_handler = logging.StreamHandler()

            formatter = logging.Formatter(
                fmt="%(asctime)s - [%(levelname)s] - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

        self.log_file = log_file
        self._loaded = True

    def get_logs(self) -> str:
        if self.log_file.exists():
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                self.logger.error(f"{e}\nНе могу прочитать лог-файл.") 
                return f"{e}\nОШИБКА ЧТЕНИЯ ЛОГА."
        return ""

    def clear_logs(self):
        if self.log_file.exists():
            try:
                open(self.log_file, "w", encoding="utf-8").close()
            except Exception as e:
                self.logger.error(f"{e}\nНе удалось очистить лог-файл.")