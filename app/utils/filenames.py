import re
from pathlib import Path


def sanitize_filename(filename: str) -> str:
    filename = Path(filename).name
    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

    if not filename:
        filename = "uploaded_file"

    return filename