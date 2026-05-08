from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse, FileResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import random
from pathlib import Path
import shutil
import uuid
import re
from app.database import init_db, get_connection
from datetime import datetime
import socket
import qrcode
from io import BytesIO


app = FastAPI()

init_db()

templates = Jinja2Templates(directory="app/templates")


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def generate_room_code():
    return str(random.randint(100000, 999999))

def sanitize_filename(filename: str)-> str:
    filename = Path(filename).name
    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
    
    if not filename:
        filename = "uploaded_file"
    
    return filename

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

def get_file(file_id: str, room_code: str):
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(
         "SELECT * FROM files WHERE id = ? AND room_code = ?",
        (file_id, room_code)
    )
    
    file = cursor.fetchone()
    connection.close()
    
    return file


def get_local_ip():
    try:
        socket_connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_connection.connect(("8.8.8.8", 80))
        local_ip = socket_connection.getsockname()[0]
        socket_connection.close()
        return local_ip
    except Exception:
        return "127.0.0.1"
    

def get_server_url():
    local_ip = get_local_ip()
    return f"http://{local_ip}:8000"


@app.get("/")
def home(request: Request):
    server_url = get_server_url()
    
    return templates.TemplateResponse(
       name="index.html",
       request=request,
       context={
           "server_url": server_url
       }
    )

@app.get("/qr")
def qr_code():
    server_url = get_server_url()
    
    qr_image = qrcode.make(server_url)
    image_buffer = BytesIO()
    qr_image.save(image_buffer, format="PNG")
    image_buffer.seek(0)
    
    return StreamingResponse(
        image_buffer,
        media_type="image/png"
    )
    
@app.post("/rooms")
def create_room(room_name: str = Form(...)):
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
    
    return RedirectResponse(
        url=f"/rooms/{room_code}",
        status_code=303
    )
    
    
@app.post("/rooms/join")
def join_room(request: Request, room_code: str = Form(...)):
    room_code = room_code.strip()
    
    if get_room(room_code) is None:
        return templates.TemplateResponse(
            name="index.html",
            request=request,
            context={
                "error": "Room not found"
            }
        ) 
         
    return RedirectResponse(
        url=f"/rooms/{room_code}",
        status_code=303
    ) 
    
    
@app.get("/rooms/{room_code}")
def room_page(request: Request, room_code: str):
    room = get_room(room_code)
    
    if room is None:
        return templates.TemplateResponse(
            name="index.html",
            request=request,
            context={
                "error": "Room not found"
            }
        )
        
    room_files = get_room_files(room_code)
    
    return templates.TemplateResponse(
        name="room.html",
        request=request,
        context={
            "room_code": room_code,
            "room_name": room["name"],
            "files": room_files
        }
    )
    
    
@app.post("/api/rooms/{room_code}/files")
def upload_file(room_code: str, uploaded_file: UploadFile = File(...)):
    if get_room(room_code) is None:
        return {"error": "Room not found"}
    
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
    
    return RedirectResponse(
        url=f"/rooms/{room_code}",
        status_code=303
    )
    
    
    
@app.get("/api/rooms/{room_code}/files/{file_id}/download")
def download_file(room_code: str, file_id: str):
    if get_room(room_code) is None:
        return {"error": "Room not found"}

    file_info = get_file(file_id, room_code)

    if file_info is None:
        return {"error": "File not found"}

    file_path = UPLOAD_DIR / room_code / file_info["stored_name"]

    if not file_path.exists() or not file_path.is_file():
        return {"error": "File missing from disk"}

    return FileResponse(
        path=file_path,
        filename=file_info["original_name"],
        media_type="application/octet-stream"
    )
    
@app.post("/api/rooms/{room_code}/files/{file_id}/delete")
def delete_file(room_code: str, file_id: str):
    if get_room(room_code) is None:
        return {"error": "Room not found"}

    file_info = get_file(file_id, room_code)

    if file_info is None:
        return RedirectResponse(
            url=f"/rooms/{room_code}",
            status_code=303
        )

    file_path = UPLOAD_DIR / room_code / file_info["stored_name"]

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

    return RedirectResponse(
        url=f"/rooms/{room_code}",
        status_code=303
    )

@app.post("/rooms/{room_code}/close")
def close_room(room_code: str):
    room = get_room(room_code)
    
    if room is None:
        return RedirectResponse(
            url="/",
            status_code=303
        )
        
    room_upload_dir = UPLOAD_DIR / room_code
    
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        "DELETE FROM files WHERE room_code = ?",
        (room_code,)
    )
    
    connection.commit()
    connection.close()
    
    if room_upload_dir.exists() and room_upload_dir.is_dir():
        shutil.rmtree(room_upload_dir)
        
    return RedirectResponse(
        url="/",
        status_code=303
    )