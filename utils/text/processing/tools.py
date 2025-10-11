import re


def crop_text(text: str, percent_crop: float) -> str:
    text = text.split(' ')
    percent_crop = round(len(text)*percent_crop)
    return ' '.join(text[percent_crop:]) + '...'

def extract_parts_by_pipe(text: str, command: str) -> list[str] | None:
    if command not in text:
        return None
    return [part.strip().strip("[]") for part in text.replace(command, "").split("|")]

def split_text(text: str, max_length: int) -> list[str]:
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

def parse_comma_list(text: str) -> list[str]:
    return [part.strip() for part in text.split(",") if part.strip()]

def format_user_record(user: dict) -> str:
    bus_info = f"**Автобус:** {user.get('bus_number')}\n" if user.get('role') == "driver" else ""
    return (
        f"**Имя:** {user.get('name')}\n"
        f"**Роль:** {translate_role(user.get('role'))}\n"
        f"**Телефон:** `+{user.get('phone_number')}`\n"
        f"**User ID:** `{user.get('user_id')}`\n"
        f"{bus_info}"
        "————————————————"
    )

def normalize_identifier(identifier: str) -> str:
    return re.sub(r'[ +—–-]', '', identifier)

def translate_role(role: str) -> str:
    match role.lower():
        case "admin":
            return "Администратор"
        case "driver":
            return "Водитель"
        case _:
            return "Ошибка перевода"