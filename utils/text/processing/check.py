from datetime import datetime
import re


PHONE_RE = re.compile(r'^\d{7,15}$')
#NAME_RE = re.compile(r'^[^\W\d_]{2,30}+(?: [^\W\d_]{2,30}+){0,3}$', re.UNICODE)
#BUS_NUMBER_RE = re.compile(r'^[a-zA-Zа-яА-Я0-9\-–—]+$', re.UNICODE)
#STOP_NAME_RE = re.compile(r'^(\s*[\w\d–—\-]{1,40}\s*){1,10}$', re.UNICODE)
NAME_RE = re.compile(r'^.+$', re.UNICODE)
BUS_NUMBER_RE = re.compile(r'^.+$', re.UNICODE)
STOP_NAME_RE = re.compile(r'^.+$', re.UNICODE)
ALLOWED_ROLES = {"admin", "driver"}

def validate_phone(phone_number: str) -> bool:
    return bool(PHONE_RE.match(phone_number))

def validate_role(role: str) -> bool:
    return role in ALLOWED_ROLES

def validate_name(name: str) -> bool:
    return bool(NAME_RE.match(name))

def validate_bus_number(bus_number: str) -> bool:
    return bool(BUS_NUMBER_RE.match(bus_number))

def validate_stop_name(stop_name: str) -> bool:
    return bool(STOP_NAME_RE.match(stop_name))

def validate_date(date_string, date_format="%Y-%m-%d"):
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False