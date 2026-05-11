from datetime import datetime
from pathlib import Path
import shutil
import uuid

from fastapi import UploadFile

from app.database import get_connection
from app.utils.filenames import sanitize_filename


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def save_uploaded_file(room_code: str, uploaded_file: UploadFile):
    room_upload_dir = UPLOAD_DIR / room_code
    room_upload_dir.mkdir(exist_ok=True)

    original_name = uploaded_file.filename or "uploaded_file"
    safe_name = sanitize_filename(original_name)

    file_id = uuid.uuid4().hex[:8]
    stored_name = f"{file_id}_{safe_name}"

    file_path = room_upload_dir / stored_name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO files (id, room_code, original_name, stored_name, uploaded_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            file_id,
            room_code,
            original_name,
            stored_name,
            datetime.now().isoformat(timespec="seconds")
        )
    )

    connection.commit()
    connection.close()

    return file_id


def get_file(file_id: str, room_code: str):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM files WHERE id = ? AND room_code = ?",
        (file_id, room_code)
    )

    file = cursor.fetchone()
    connection.close()

    if file is None:
        return None

    file_path = UPLOAD_DIR / room_code / file["stored_name"]

    return {
        "id": file["id"],
        "room_code": file["room_code"],
        "original_name": file["original_name"],
        "stored_name": file["stored_name"],
        "uploaded_at": file["uploaded_at"],
        "file_path": file_path
    }


def delete_file(file_id: str, room_code: str):
    file_info = get_file(file_id, room_code)

    if file_info is None:
        return

    file_path = file_info["file_path"]

    if file_path.exists() and file_path.is_file():
        file_path.unlink()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM files WHERE id = ? AND room_code = ?",
        (file_id, room_code)
    )

    connection.commit()
    connection.close()