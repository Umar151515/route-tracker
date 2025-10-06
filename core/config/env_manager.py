import os

from dotenv import load_dotenv

from .paths import env_path


class EnvManager:
    _instance: "EnvManager" = None
    _default_env = """# Please fill in these values
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GOOGLE_SHEET_NAME=Лист1
GOOGLE_SHEET_ID=your_google_sheet_id_here"""

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_loaded'):
            self._loaded = False
            self.load()

    def load(self):
        if not env_path.exists():
            with open(env_path, 'w', encoding="utf-8") as file:
                file.write(self._default_env)
            raise FileNotFoundError(
                f"Env file was not found at {env_path}\n"
                "A new env file has been created with default values.\n"
                "Please fill in the required configuration in this file\n"
                "before running the application again."
            )
        load_dotenv(env_path)
        self._loaded = True

    def _ensure_loaded(self):
        if not self._loaded:
            raise RuntimeError("Environment variables not loaded. Call load() first")

    def has(self, key: str) -> bool:
        self._ensure_loaded()
        return key in os.environ

    def get(self, key: str, default:str|None = None) -> str:
        self._ensure_loaded()
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Environment variable '{key}' not set and no default provided")
        return value
    
    def set(self, key: str, value: str):
        self._ensure_loaded()
        os.environ[key] = value
    
    def __getitem__(self, key: str) -> str:
        return self.get(key)

    def __setitem__(self, key: str, value: str):
        self.set(key, value)