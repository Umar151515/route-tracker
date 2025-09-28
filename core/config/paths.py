from pathlib import Path


config_folder_path = Path("configs")
config_folder_path.mkdir(parents=True, exist_ok=True)

data_folder_path = Path("data")
data_folder_path.mkdir(parents=True, exist_ok=True)

env_path = config_folder_path / ".env"
app_config_path = config_folder_path / "app.json"

data_path = data_folder_path / "data.db"
data_path.touch(exist_ok=True)

__all__ = [
    'config_folder_path', 
    'env_path',
    "app_config_path",
    'data_folder_path', 
    'data_path'
]