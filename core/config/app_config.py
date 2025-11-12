from .paths import app_config_path
from .key_value_base import KeyValueBase


class AppConfig(KeyValueBase):
    config_path = app_config_path
    keys = {"time_zone": str, "min_passenger_count": int, "max_passenger_count": int}