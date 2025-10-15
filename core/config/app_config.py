from .paths import app_config_path
from .key_value_base import KeyValueBase


class AppConfig(KeyValueBase):
    config_path = app_config_path
    _keys = ["time_zone", "min_passenger_count", "max_passenger_count"]