import time
import logging
import concurrent.futures
import jwt
import html
import re
import urllib.parse

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

# spam protection
user_message_count = {}

CHAT_COOLDOWN = 0.5
COMMAND_COOLDOWN = 3

MESSAGE_WINDOW = 5
MAX_MESSAGES = 20


# ---------------- JWT ----------------

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        return None


def get_current_user():
    return connected_users.get(request.sid)


# ---------------- SECURITY ----------------

def sanitize(text):
    if not text:
        return ""

    text = text.strip()

    text = html.escape(text, quote=True)

    if len(text) > 300:
        text = text[:300]

    return text


def is_safe_url(url):

    try:
        parsed = urllib.parse.urlparse(url)

        host = parsed.hostname

        if not host:
            return False

        # block localhost
        if host in ["127.0.0.1", "localhost"]:
            return False

        # block private networks
        private_patterns = [
            r"^10\.",
            r"^172\.(1[6-9]|2[0-9]|3[0-1])\.",
            r"^192\.168\."
        ]

        for pattern in private_patterns:
            if re.match(pattern, host):
                return False

        return True

    except Exception:
        return False


# ---------------- RATE LIMIT ----------------

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


def is_spamming(user_id):

    now = time.time()

    if user_id not in user_message_count:
        user_message_count[user_id] = []

    timestamps = user_message_count[user_id]

    timestamps.append(now)

    user_message_count[user_id] = [
        t for t in timestamps if now - t < MESSAGE_WINDOW
    ]

    if len(user_message_count[user_id]) > MAX_MESSAGES:
        return True

    return False


def handle_connect():

    token = request.cookies.get("token")

    if not token:
        logging.warning("[SECURITY] Rejected connection: Missing token")
        return False

    payload = verify_token(token)

    if not payload:
        logging.warning("[SECURITY] Rejected connection: Invalid token")
        return False

    connected_users[request.sid] = payload

    logging.info(f"User connected: {payload['username']}")

# ---------------- CONNECT ----------------

def handle_connect():

    token = request.cookies.get("token")

    if not token:
        logging.warning("[SECURITY] Rejected connection: Missing token")
        return False

    payload = verify_token(token)

    if not payload:
        logging.warning("[SECURITY] Rejected connection: Invalid token")
        return False

    connected_users[request.sid] = payload

    logging.info(f"User connected: {payload['username']}")

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


# ---------------- CHAT ----------------

def handle_chat(socketio, data):

    room = str(data.get("room"))

    raw_msg = data.get("msg", "")

    msg = sanitize(raw_msg)

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

    # spam detection
    if is_spamming(user_id):
        emit("chat", {
            "username": "System",
            "msg": "You are sending messages too fast."
        })
        disconnect()
        return

    # commands
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

            # SSRF protection
            if query.startswith("http"):
                if not is_safe_url(query):
                    socketio.emit(
                        "chat",
                        {"username": "System", "msg": "Blocked unsafe URL."},
                        room=room
                    )
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

    # basic rate limit
    if is_chat_rate_limited(user_id):
        return

    socketio.emit(
        "chat",
        {"username": username, "msg": msg},
        room=room
    )