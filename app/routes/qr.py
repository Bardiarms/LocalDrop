from io import BytesIO

import qrcode
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.utils.network import get_server_url


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