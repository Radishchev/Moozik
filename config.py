import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

# load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HLS_ROOT = os.path.join(BASE_DIR, "hls")

FFMPEG_PATH = "ffmpeg"

DATABASE_PATH = os.path.join(BASE_DIR, "users.db")

JWT_SECRET = os.getenv("JWT_SECRET")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

if not JWT_SECRET:
    raise Exception("JWT_SECRET environment variable not set!")

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_SECONDS = 86400