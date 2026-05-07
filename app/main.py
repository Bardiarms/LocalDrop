from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import random

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

rooms = {}

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
    
    return templates.TemplateResponse(
        name="room.html",
        request=request,
        context={
            "room_code": room_code,
            "room_name": room["name"]
        }
    )