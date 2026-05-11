from datetime import datetime
import shutil
from pathlib import Path

from app.database import get_connection
from app.utils.rooms import generate_room_code


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def get_room(room_code: str):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM rooms WHERE code = ?",
        (room_code,)
    )

    room = cursor.fetchone()
    connection.close()

    return room


def get_room_files(room_code: str):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM files WHERE room_code = ? ORDER BY uploaded_at DESC",
        (room_code,)
    )

    rows = cursor.fetchall()
    connection.close()

    return rows


def create_room_record(room_name: str) -> str:
    room_code = generate_room_code()

    while get_room(room_code) is not None:
        room_code = generate_room_code()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO rooms (code, name, created_at)
        VALUES (?, ?, ?)
        """,
        (
            room_code,
            room_name,
            datetime.now().isoformat(timespec="seconds")
        )
    )

    connection.commit()
    connection.close()

    room_upload_dir = UPLOAD_DIR / room_code
    room_upload_dir.mkdir(exist_ok=True)

    return room_code


def close_room(room_code: str):
    room = get_room(room_code)

    if room is None:
        return

    room_upload_dir = UPLOAD_DIR / room_code

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM files WHERE room_code = ?",
        (room_code,)
    )

    cursor.execute(
        "DELETE FROM rooms WHERE code = ?",
        (room_code,)
    )

    connection.commit()
    connection.close()

    if room_upload_dir.exists() and room_upload_dir.is_dir():
        shutil.rmtree(room_upload_dir)