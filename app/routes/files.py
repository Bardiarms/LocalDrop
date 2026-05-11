from fastapi import APIRouter, UploadFile, File
from fastapi.responses import RedirectResponse, FileResponse

from app.services.room_service import get_room
from app.services.file_service import save_uploaded_file, get_file, delete_file


router = APIRouter()


@router.post("/api/rooms/{room_code}/files")
def upload_file(room_code: str, uploaded_file: UploadFile = File(...)):
    if get_room(room_code) is None:
        return {"error": "Room not found"}

    save_uploaded_file(room_code, uploaded_file)

    return RedirectResponse(
        url=f"/rooms/{room_code}",
        status_code=303
    )


@router.get("/api/rooms/{room_code}/files/{file_id}/download")
def download_file(room_code: str, file_id: str):
    if get_room(room_code) is None:
        return {"error": "Room not found"}

    file_info = get_file(file_id, room_code)

    if file_info is None:
        return {"error": "File not found"}

    file_path = file_info["file_path"]

    if not file_path.exists() or not file_path.is_file():
        return {"error": "File missing from disk"}

    return FileResponse(
        path=file_path,
        filename=file_info["original_name"],
        media_type="application/octet-stream"
    )


@router.post("/api/rooms/{room_code}/files/{file_id}/delete")
def delete_file_route(room_code: str, file_id: str):
    if get_room(room_code) is None:
        return {"error": "Room not found"}

    delete_file(file_id, room_code)

    return RedirectResponse(
        url=f"/rooms/{room_code}",
        status_code=303
    )