import os
import logging
from flask import Flask, request, send_from_directory, render_template
from flask_cors import CORS
from flask_socketio import SocketIO

from config import HLS_ROOT
import socket_handlers

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', 
                    logger=True, engineio_logger=True, ping_timeout=60)

@app.route('/')
def index():
    return render_template('index.html')

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
def handle_connect():
    logging.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    logging.info(f"Client disconnected: {request.sid}")

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
