from flask import Blueprint, request, jsonify, make_response
import jwt
import datetime
import bcrypt

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_SECONDS, GOOGLE_CLIENT_ID
from models import create_user, get_user_by_username, get_user_by_id

auth_bp = Blueprint("auth", __name__)


# ---------------- PASSWORD SECURITY ----------------

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password, hashed_password):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# ---------------- JWT ----------------

def generate_token(user):

    payload = {
        "user_id": user["id"],
        "username": user["username"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(
            seconds=JWT_EXPIRATION_SECONDS
        )
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token


def verify_token(token):

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None


def get_token_from_cookie(req):
    return req.cookies.get("token")


# ---------------- REGISTER ----------------

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

    hashed_password = hash_password(password)

    create_user(username, email, hashed_password)

    user = get_user_by_username(username)

    token = generate_token(user)

    response = make_response(jsonify({
        "username": user["username"],
        "avatar_color": "#4F46E5"
    }))

    response.set_cookie(
        "token",
        token,
        httponly=True,
        secure=False,  # change to True in production
        samesite="Strict",
        max_age=JWT_EXPIRATION_SECONDS
    )

    return response


# ---------------- LOGIN ----------------

@auth_bp.route("/api/login", methods=["POST"])
def login():

    data = request.json

    username = data.get("username")
    password = data.get("password")

    user = get_user_by_username(username)

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not verify_password(password, user["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(user)

    response = make_response(jsonify({
        "username": user["username"],
        "avatar_color": "#4F46E5"
    }))

    response.set_cookie(
        "token",
        token,
        httponly=True,
        secure=False,
        samesite="Strict",
        max_age=JWT_EXPIRATION_SECONDS
    )

    return response


# ---------------- GOOGLE LOGIN ----------------

@auth_bp.route("/api/google-login", methods=["POST"])
def google_login():

    data = request.json
    credential = data.get("credential")

    if not credential:
        return jsonify({"error": "Missing credential"}), 400

    try:

        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")

        if not email:
            return jsonify({"error": "Invalid Google account"}), 400

        # check if user exists
        user = get_user_by_username(email)

        if not user:

            # create user automatically
            create_user(
                username=email,
                email=email,
                password="GOOGLE_AUTH"
            )

            user = get_user_by_username(email)

        token = generate_token(user)

        response = make_response(jsonify({
            "username": user["username"],
            "avatar_color": "#4F46E5"
        }))

        response.set_cookie(
            "token",
            token,
            httponly=True,
            secure=False,
            samesite="Strict",
            max_age=JWT_EXPIRATION_SECONDS
        )

        return response

    except ValueError:
        return jsonify({"error": "Invalid Google token"}), 401


# ---------------- LOGOUT ----------------

@auth_bp.route("/api/logout", methods=["POST"])
def logout():

    response = make_response(jsonify({"message": "Logged out"}))

    response.delete_cookie("token")

    return response


# ---------------- CURRENT USER ----------------

@auth_bp.route("/api/me")
def me():

    token = get_token_from_cookie(request)

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