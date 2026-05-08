from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
import random
from pathlib import Path
import shutil
import uuid
import re

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

rooms = {}

files = {}

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

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
       name="index.html",
       request=request
    )
    
@app.post("/rooms")
def create_room(room_name: str = Form(...)):
    room_code = generate_room_code()

    while room_code in rooms:
        room_code = generate_room_code()
    
    rooms[room_code] = {
        "name": room_name
    }
    
    files[room_code] = {}
    
    return RedirectResponse(
        url=f"/rooms/{room_code}",
        status_code=303
    )
    
@app.post("/rooms/join")
def join_room(request: Request, room_code: str = Form(...)):
    room_code = room_code.strip()
    
    if room_code not in rooms:
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
    if room_code not in rooms:
        return templates.TemplateResponse(
            name="index.html",
            request=request,
            context={
                "error": "Room not found"
            }
        )
    room = rooms[room_code]
    
    room_files = files.get(room_code, {})
    
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
    if room_code not in rooms:
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
        
    if room_code not in files:
        files[room_code] = {}
        
    files[room_code][file_id] = {
        "original_name": original_name,
        "stored_name": stored_name
    }
    
    return RedirectResponse(
        url=f"/rooms/{room_code}",
        status_code=303
    )
    
    
    
@app.get("/api/rooms/{room_code}/files/{file_id}/download")
def download_file(room_code: str, file_id: str):
    if room_code not in rooms:
        return {"error": "Room not found"}

    room_files = files.get(room_code, {})

    if file_id not in room_files:
        return {"error": "File not found"}

    file_info = room_files[file_id]
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
    if room_code not in rooms:
        return {"error": "Room not found"}

    room_files = files.get(room_code, {})

    if file_id not in room_files:
        return RedirectResponse(
            url=f"/rooms/{room_code}",
            status_code=303
        )

    file_info = room_files[file_id]
    file_path = UPLOAD_DIR / room_code / file_info["stored_name"]

    if file_path.exists() and file_path.is_file():
        file_path.unlink()

    del room_files[file_id]

    return RedirectResponse(
        url=f"/rooms/{room_code}",
        status_code=303
    )
