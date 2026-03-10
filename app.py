import os
import logging

from flask import Flask, send_from_directory, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO

from config import HLS_ROOT
from database import init_db
from auth_routes import auth_bp

import socket_handlers

app = Flask(__name__)
CORS(app)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
    logger=True,
    engineio_logger=True,
    ping_timeout=60
)

# initialize database
init_db()

# register auth routes
app.register_blueprint(auth_bp)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/chat")
def chat():
    return render_template("chat.html")


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

    token = None

    if auth:
        token = auth.get("token")

    if not token:
        logging.info("Connection rejected: No token")
        return False

    payload = verify_token(token)

    if not payload:
        logging.info("Connection rejected: Invalid token")
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
