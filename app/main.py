from fastapi import FastAPI

from app.database import init_db
from app.routes import pages, rooms, files, qr


app = FastAPI()

init_db()

app.include_router(pages.router)
app.include_router(rooms.router)
app.include_router(files.router)
app.include_router(qr.router)