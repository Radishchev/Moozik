import os
import logging

logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HLS_ROOT = os.path.join(BASE_DIR, "hls")

FFMPEG_PATH = "ffmpeg"

DATABASE_PATH = os.path.join(BASE_DIR, "users.db")

JWT_SECRET = "H0gfNpU8Az5lUWxeu6deVaYVMX6X5vd1MI0xaqu433J"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_SECONDS = 86400
