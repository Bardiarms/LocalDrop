from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.services.room_service import get_room, get_room_files
from app.utils.network import get_server_url


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home(request: Request):
    server_url = get_server_url()

    return templates.TemplateResponse(
        name="index.html",
        request=request,
        context={
            "server_url": server_url
        }
    )


@router.get("/rooms/{room_code}")
def room_page(request: Request, room_code: str):
    room = get_room(room_code)

    if room is None:
        return templates.TemplateResponse(
            name="index.html",
            request=request,
            context={
                "error": "Room not found",
                "server_url": get_server_url()
            }
        )

    room_files = get_room_files(room_code)

    return templates.TemplateResponse(
        name="room.html",
        request=request,
        context={
            "room_code": room_code,
            "room_name": room["name"],
            "files": room_files,
            "server_url": get_server_url()
        }
    )