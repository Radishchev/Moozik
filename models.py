from database import get_db


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
