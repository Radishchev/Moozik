import os
import logging

from flask import Flask, send_from_directory, render_template, request, redirect
from flask_cors import CORS
from flask_socketio import SocketIO

from config import HLS_ROOT
from database import init_db
from auth_routes import auth_bp
from room_routes import room_bp
from models import get_room_by_code

import socket_handlers


app = Flask(__name__)
CORS(app)

ALLOWED_ORIGINS = [
    "http://localhost:5000",
    "http://127.0.0.1:5000"
]

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
    logger=True,
    engineio_logger=True,
    ping_timeout=60
)

init_db()

app.register_blueprint(auth_bp)
app.register_blueprint(room_bp)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/rooms")
def rooms_page():
    return render_template("rooms.html")


@app.route("/room/<room_code>")
def room_page(room_code):

    room = get_room_by_code(room_code)

    if not room:
        return redirect("/rooms")

    return render_template(
        "chat.html",
        room_code=room_code,
        room_name=room["name"]
    )


@app.route('/hls/<room>/<path:filename>')
def serve_hls(room, filename):

    path = os.path.join(HLS_ROOT, room, filename)

    if not os.path.isfile(path):
        return 'Not Found', 404

    resp = send_from_directory(os.path.join(HLS_ROOT, room), filename)

    resp.headers.update({
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    })

    return resp


@socketio.on('connect')
def handle_connect(auth):

    from socket_handlers import verify_token, connected_users

    origin = request.headers.get("Origin")

    if origin not in ALLOWED_ORIGINS:
        logging.warning(f"[SECURITY] Rejected connection from origin: {origin}")
        return False

    token = None

    if auth:
        token = auth.get("token")

    if not token:
        logging.warning("[SECURITY] Rejected connection: No token")
        return False

    payload = verify_token(token)

    if not payload:
        logging.warning("[SECURITY] Rejected connection: Invalid token")
        return False

    connected_users[request.sid] = payload

    logging.info(f"User connected: {payload['username']}")


@socketio.on('disconnect')
def handle_disconnect():

    from socket_handlers import connected_users

    if request.sid in connected_users:
        user = connected_users.pop(request.sid)
        logging.info(f"{user['username']} disconnected")


@socketio.on('join')
def on_join(data):
    socket_handlers.handle_join(socketio, data)


@socketio.on('check_stream')
def on_check_stream(data):
    socket_handlers.handle_check_stream(data)


@socketio.on('chat')
def on_chat(data):
    socket_handlers.handle_chat(socketio, data)


if __name__ == '__main__':

    os.makedirs(HLS_ROOT, exist_ok=True)

    socketio.run(app, host='0.0.0.0', port=5000)
