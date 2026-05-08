# LocalDrop

LocalDrop is a small local-network file transfer web app built with FastAPI.

I developed this project for my own personal file-transfer tasks in addition to having some fun and some hands-on experience with FastAPI. The idea is simple: run the server on one computer, then let other devices on the same local network connect through a browser to upload, download, and share files.

## Features

- Create and join transfer rooms
- Upload files to a room
- List uploaded files
- Download files from another device
- Delete individual files
- Close a room and clean up its files
- SQLite-based metadata storage
- QR code generation for easier connection
- Works over a local network

## Tech Stack

- Python
- FastAPI
- SQLite
- Jinja2 templates
- qrcode

## Running the Project

Create and activate a virtual environment:

```bash
python -m venv env
source env/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open the app on your computer:

```text
http://127.0.0.1:8000
```

Other devices on the same network can connect using the displayed local network address or QR code.

## Important Note

This project is intended for trusted local networks and personal use. The current version is not safe to be exposed directly to the public internet.(Maybe in the future more secure transfer protocols will be added.)

