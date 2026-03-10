from flask import Blueprint, request, jsonify
import jwt
import datetime

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_SECONDS
from models import create_user, get_user_by_username, get_user_by_id

auth_bp = Blueprint("auth", __name__)


def generate_token(user):
    payload = {
        "user_id": user["id"],
        "username": user["username"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXPIRATION_SECONDS)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token


def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        return None


def get_token_from_header(request):
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ")[1]
    return None


@auth_bp.route("/api/register", methods=["POST"])
def register():

    data = request.json

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    existing = get_user_by_username(username)
    if existing:
        return jsonify({"error": "Username already exists"}), 400

    # plaintext password intentionally (iteration 1)
    create_user(username, email, password)

    user = get_user_by_username(username)

    token = generate_token(user)

    return jsonify({
        "token": token,
        "username": user["username"],
        "avatar_color": "#4F46E5"
    })


@auth_bp.route("/api/login", methods=["POST"])
def login():

    data = request.json

    username = data.get("username")
    password = data.get("password")

    user = get_user_by_username(username)

    if not user or user["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(user)

    return jsonify({
        "token": token,
        "username": user["username"],
        "avatar_color": "#4F46E5"
    })


@auth_bp.route("/api/me")
def me():

    token = get_token_from_header(request)

    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    payload = verify_token(token)

    if not payload:
        return jsonify({"error": "Invalid token"}), 401

    user = get_user_by_id(payload["user_id"])

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "username": user["username"],
        "email": user["email"],
        "avatar_color": "#4F46E5"
    })
