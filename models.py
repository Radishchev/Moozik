import secrets
import string

from database import get_db


# ---------------- USERS ----------------

def create_user(username, email, password):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (username, email, password)
    )

    conn.commit()
    conn.close()


def get_user_by_username(username):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    user = cur.fetchone()

    conn.close()

    return user


def get_user_by_id(user_id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, username, email FROM users WHERE id=?",
        (user_id,)
    )

    user = cur.fetchone()

    conn.close()

    return user


# ---------------- ROOM CODE GENERATOR ----------------

def generate_room_code(length=8):

    alphabet = string.ascii_letters

    return ''.join(secrets.choice(alphabet) for _ in range(length))


# ---------------- ROOMS ----------------

def create_room(name, owner_id, is_private):

    conn = get_db()
    cur = conn.cursor()

    room_code = generate_room_code()

    invite_code = None

    if is_private:
        invite_code = generate_room_code()

    cur.execute("""
        INSERT INTO rooms (name, code, owner_id, is_private, invite_code)
        VALUES (?, ?, ?, ?, ?)
    """, (name, room_code, owner_id, int(is_private), invite_code))

    conn.commit()
    conn.close()

    return {
        "room_code": room_code,
        "invite_code": invite_code
    }


def get_public_rooms():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT name, code FROM rooms
        WHERE is_private = 0
    """)

    rooms = cur.fetchall()

    conn.close()

    return rooms


def get_room_by_code(code):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM rooms WHERE code=?",
        (code,)
    )

    room = cur.fetchone()

    conn.close()

    return room


def get_room_by_code_or_invite(value):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM rooms WHERE code=? OR invite_code=?",
        (value, value)
    )

    room = cur.fetchone()

    conn.close()

    return room