import re

PHONE_RE = re.compile(r'^\d{7,15}$')
NAME_RE = re.compile(r'^[^\W\d_]{2,30}+(?: [^\W\d_]{2,30}+){0,3}$', re.UNICODE)
ALLOWED_ROLES = {"admin", "driver"}

def validate_phone(phone_number: str) -> bool:
    return bool(PHONE_RE.match(phone_number))

def validate_role(role: str) -> bool:
    return role in ALLOWED_ROLES

def validate_name(name: str) -> bool:
    return bool(NAME_RE.match(name))