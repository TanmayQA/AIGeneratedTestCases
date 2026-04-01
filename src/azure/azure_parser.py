import re
from typing import Optional


def extract_work_item_id(value: str) -> Optional[int]:
    if not value:
        return None

    value = value.strip()

    if value.isdigit():
        return int(value)

    match = re.search(r"/_workitems/edit/(\d+)", value)
    if match:
        return int(match.group(1))

    match = re.search(r"\b(\d{4,})\b", value)
    if match:
        return int(match.group(1))

    return None