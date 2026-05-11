# LocalDrop

LocalDrop is a small local-network file transfer web app built with FastAPI.

I developed this project for my own personal file-transfer tasks in addition to having some fun and some hands-on experience with FastAPI. The idea is simple: run the server on one computer, then let other devices on the same local network connect through a browser to upload, download, and share files.

## Features

- Create and join transfer rooms
- Upload files to a room
- Show upload and download progress
- List uploaded files
- Download files from another device
- Delete individual files
- Close a room and clean up its files
- SQLite-based metadata storage
- QR code generation for easier connection
- Room-specific QR codes for direct room access
- Works over a local network

## Tech Stack

- Python
- FastAPI
- SQLite
- Jinja2 templates
- JavaScript
- qrcode

## Running the Project

Create and activate a virtual environment:

```bash
python -m venv env
source env/bin/activate
```

Install the project in editable mode:

```bash
pip install -e .
```

This installs LocalDrop as a local command-line tool.

Run the server:

```bash
localdrop
```

Then open the app on your computer:

```text
http://127.0.0.1:8000
```

Other devices on the same network can connect using the displayed local network address or QR code.

## Development Mode

If you are actively editing the code and want automatic reloads, you can run the app with Uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Project Packaging

LocalDrop includes a `pyproject.toml` file so it can be installed locally using:

```bash
pip install -e .
```

The command-line entry point is configured as:

```text
localdrop
```

So after installation, the server can be started with it.


## Important Note

This project is intended for trusted local networks and personal use. The current version is not safe to be exposed directly to the public internet. Maybe in the future, more secure transfer protocols will be added.