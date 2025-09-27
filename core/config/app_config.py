from .paths import app_config_path
from .key_value_base import KeyValueBase


class AppConfig(KeyValueBase):
    config_path = app_config_path
    _keys = []