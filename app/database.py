import sqlite3
from pathlib import Path


DB_PATH = Path("localdrop.db")

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(
    """
        CREATE TABLE IF NOT EXISTS rooms (
            code TEXT PRIMARY KEY,
            name NOT NULL,
            created_at TEXT NOT NULL
        )
    """
    )
    
    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS files (
        id TEXT PRIMARY KEY,
        room_code  TEXT NOT NULL,
        original_name TEXT NOT NULL,
        stored_name TEXT NOT NULL,
        uploaded_at TEXT NOT NULL,
        FOREIGN KEY (room_code) REFERENCES rooms(code)
    )
    """
    )
    
    connection.commit()
    connection.close()
    