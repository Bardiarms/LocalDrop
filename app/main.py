from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
import random
from pathlib import Path
import shutil


app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

rooms = {}

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def generate_room_code():
    return str(random.randint(100000, 999999))

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
    
    room_upload_dir = UPLOAD_DIR / room_code
    room_upload_dir.mkdir(exist_ok=True)
    
    files = []
    
    for file_path in room_upload_dir.iterdir():
        if file_path.is_file():
            files.append(file_path.name)
    
    return templates.TemplateResponse(
        name="room.html",
        request=request,
        context={
            "room_code": room_code,
            "room_name": room["name"],
            "files": files
        }
    )
    
    
@app.post("/api/rooms/{room_code}/files")
def upload_file(room_code: str, uploaded_file: UploadFile = File(...)):
    if room_code not in rooms:
        return {"error": "Room not found"}
    
    room_upload_dir = UPLOAD_DIR / room_code
    room_upload_dir.mkdir(exist_ok=True)
    
    file_path = room_upload_dir / uploaded_file.filename
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
        
    return RedirectResponse(
        url=f"/rooms/{room_code}",
        status_code=303
    )
    
    
    
@app.get("/api/rooms/{room_code}/files/{filename}/download")
def download_file(room_code: str, filename: str):
    if room_code not in rooms:
        return {"error": "Room not found"}
    
    file_path = UPLOAD_DIR / room_code / filename
    
    if not file_path.exists() or not file_path.is_file():
        return {"error": "File not found"}
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )
    
@app.post("/api/rooms/{room_code}/files/{filename}/delete")
def delete_file(room_code: str, filename: str):
    if room_code not in rooms:
        return {"error": "Room not found"}
    
    file_path = UPLOAD_DIR / room_code / filename
    
    if file_path.exists() and file_path.is_file():
        file_path.unlink()
        
    return RedirectResponse(
        url=f"/rooms/{room_code}",
        status_code=303
    )
    
