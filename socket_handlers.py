import time
import logging
import concurrent.futures
import jwt
import html 

from flask import request
from flask_socketio import join_room, emit, disconnect

from youtube_utils import fetch_song_info
from streaming import start_hls_stream, room_streams
from config import JWT_SECRET, JWT_ALGORITHM


room_queues = {}

executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

connected_users = {}

user_last_chat = {}
user_last_command = {}

CHAT_COOLDOWN = 0.5
COMMAND_COOLDOWN = 3


def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        return None


def get_current_user():
    return connected_users.get(request.sid)


def sanitize(text):
    return html.escape(text)


def is_chat_rate_limited(user_id):
    now = time.time()
    last = user_last_chat.get(user_id, 0)

    if now - last < CHAT_COOLDOWN:
        return True

    user_last_chat[user_id] = now
    return False


def is_command_rate_limited(user_id):
    now = time.time()
    last = user_last_command.get(user_id, 0)

    if now - last < COMMAND_COOLDOWN:
        return True

    user_last_command[user_id] = now
    return False


def handle_join(socketio, data):

    room = str(data.get("room"))

    if not room:
        emit("chat", {"username": "System", "msg": "Room ID required"})
        disconnect()
        return

    user = get_current_user()

    if not user:
        emit("chat", {"username": "System", "msg": "Authentication required"})
        disconnect()
        return

    username = sanitize(user["username"])

    join_room(room)

    room_queues.setdefault(room, [])

    logging.info(f"{username} joined room {room}")

    emit(
        "chat",
        {"username": "System", "msg": f"{username} joined the room."},
        room=room
    )

    cur = room_streams.get(room)

    if cur:
        emit("song_changed", {
            "title": cur["title"],
            "thumbnail": cur["thumbnail"],
            "duration": cur["duration"]
        })

        if cur.get("status") == "streaming":
            emit(
                "stream_ready",
                {"room": room, "timestamp": time.time()}
            )


def handle_check_stream(data):

    room = str(data.get("room"))

    if not room:
        return

    cur = room_streams.get(room)

    if cur and cur.get("status") == "streaming":
        emit(
            "stream_ready",
            {"room": room, "timestamp": time.time()}
        )


def handle_chat(socketio, data):

    room = str(data.get("room"))

    raw_msg = data.get("msg", "")
    msg = sanitize(raw_msg.strip())

    if not room or not msg:
        return

    user = get_current_user()

    if not user:
        disconnect()
        return

    username = sanitize(user["username"])
    user_id = user["user_id"]

    if len(msg) > 300:
        emit("chat", {
            "username": "System",
            "msg": "Message too long."
        })
        return

    if msg.lower().startswith("!play ") or msg.lower() == "!skip":

        if is_command_rate_limited(user_id):
            emit("chat", {
                "username": "System",
                "msg": "Command cooldown active (3s)."
            })
            return

        if msg.lower().startswith("!play "):

            query = msg[6:].strip()

            if not query:
                return

            socketio.emit(
                "chat",
                {"username": "System", "msg": f'{username} requested "{query}"'},
                room=room
            )

            def handle_song():
                try:
                    song = fetch_song_info(query)

                    queue = room_queues[room]

                    if room not in room_streams or room_streams[room].get("status") != "streaming":
                        start_hls_stream(room, song, socketio)
                    else:
                        queue.append(song)

                        socketio.emit(
                            "queue_updated",
                            {"queue": [s["title"] for s in queue]},
                            room=room
                        )

                except Exception as e:
                    socketio.emit(
                        "chat",
                        {"username": "System", "msg": f"Error: {str(e)}"},
                        room=room
                    )

            executor.submit(handle_song)
            return

        if msg.lower() == "!skip":

            socketio.emit(
                "chat",
                {"username": "System", "msg": f"{username} skipped the song"},
                room=room
            )

            cur = room_streams.get(room)

            if cur:
                try:
                    cur["ffmpeg_proc"].kill()
                except Exception as e:
                    logging.error(f"Error killing ffmpeg proc: {e}")

                queue = room_queues[room]

                if queue:
                    next_song = queue.pop(0)

                    start_hls_stream(room, next_song, socketio)

                    socketio.emit(
                        "queue_updated",
                        {"queue": [s["title"] for s in queue]},
                        room=room
                    )
                else:
                    room_streams.pop(room, None)

                    socketio.emit("song_stopped", {}, room=room)

            return

    if is_chat_rate_limited(user_id):
        return

    socketio.emit(
        "chat",
        {"username": username, "msg": msg},
        room=room
    )
