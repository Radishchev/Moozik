from flask import Blueprint, request, jsonify
from models import create_room, get_public_rooms, get_room_by_code_or_invite
from auth_routes import verify_token, get_token_from_cookie

room_bp = Blueprint("rooms", __name__)


# Create a new room
@room_bp.route("/api/rooms/create", methods=["POST"])
def create():

    token = get_token_from_cookie(request)
    payload = verify_token(token)

    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    name = data.get("name")
    is_private = data.get("private", False)

    if not name:
        return jsonify({"error": "Room name required"}), 400

    room = create_room(name, payload["user_id"], is_private)

    return jsonify(room)


# Get list of public rooms
@room_bp.route("/api/rooms/public")
def public_rooms():

    rooms = get_public_rooms()

    return jsonify([
        {
            "name": r["name"],
            "code": r["code"]
        }
        for r in rooms
    ])


# Join room using code or invite code
@room_bp.route("/api/rooms/join/<code>")
def join_private(code):

    room = get_room_by_code_or_invite(code)

    if not room:
        return jsonify({"error": "Invalid code"}), 404

    return jsonify({
        "room_code": room["code"]
    })