from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routes import pages, rooms, files, qr


app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

init_db()

app.include_router(pages.router)
app.include_router(rooms.router)
app.include_router(files.router)
app.include_router(qr.router)