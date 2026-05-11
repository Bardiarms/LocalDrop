from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.room_service import create_room_record, get_room, close_room
from app.utils.network import get_server_url


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/rooms")
def create_room(room_name: str = Form(...)):
    room_code = create_room_record(room_name)

    return RedirectResponse(
        url=f"/rooms/{room_code}",
        status_code=303
    )


@router.post("/rooms/join")
def join_room(request: Request, room_code: str = Form(...)):
    room_code = room_code.strip()

    if get_room(room_code) is None:
        return templates.TemplateResponse(
            name="index.html",
            request=request,
            context={
                "error": "Room not found. Please check the code.",
                "server_url": get_server_url()
            }
        )

    return RedirectResponse(
        url=f"/rooms/{room_code}",
        status_code=303
    )


@router.post("/rooms/{room_code}/close")
def close_room_route(room_code: str):
    close_room(room_code)

    return RedirectResponse(
        url="/",
        status_code=303
    )