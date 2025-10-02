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