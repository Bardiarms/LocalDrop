import socket


def get_local_ip() -> str:
    try:
        socket_connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_connection.connect(("8.8.8.8", 80))
        local_ip = socket_connection.getsockname()[0]
        socket_connection.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def get_server_url() -> str:
    local_ip = get_local_ip()
    return f"http://{local_ip}:8000"