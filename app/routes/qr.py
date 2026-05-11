from io import BytesIO

import qrcode
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.utils.network import get_server_url, get_room_url
from app.services.room_service import get_room


router = APIRouter()


@router.get("/qr")
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
    

@router.get("/qr/rooms/{room_code}")
def room_qr_code(room_code: str):
    room = get_room(room_code)

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    room_url = get_room_url(room_code)

    qr_image = qrcode.make(room_url)

    image_buffer = BytesIO()
    qr_image.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    return StreamingResponse(
        image_buffer,
        media_type="image/png"
    )