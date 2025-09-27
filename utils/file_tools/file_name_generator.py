import re
import uuid
from datetime import datetime


def generate_file_name(prompt:str = None) -> str:
    if prompt:
        clean_prompt = re.sub(r'[^\w\s-]', '', prompt, flags=re.ASCII)[:25].strip().replace(' ', '_')
    else:
        clean_prompt = uuid.uuid4().hex[:6]
    time_part = datetime.now().strftime("%H%M%S%f")[:-3]
    return f"{clean_prompt}_{time_part}"