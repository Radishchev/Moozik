# 🎵 Moozik — Enhanced Edition

A premium real-time music & chat web app where friends listen to music together in sync.

---

## ✨ What's New

### 🔐 Authentication System
- **Register** with username, email, and password (bcrypt hashed)
- **Login** with JWT tokens (7-day expiry, stored in localStorage)
- Password strength indicator on registration
- Auto-login on page revisit

### 🎵 Music Rooms
- **Create** public or private rooms (private rooms support passwords)
- **Join** by shareable 6-character room code (e.g. `ABC123`)
- All users in a room hear the same song in sync
- Commands in room chat:
  - `!play <song name or YouTube URL>` — queue and play a song
  - `!skip` — skip current song (any member can skip)
- Song queue displayed in the player sidebar
- Album art with glowing background effect

### 💬 Chat Rooms
- **Dedicated chat rooms** separate from music rooms
- Create or join with a shareable code
- Real-time messaging via WebSocket
- Messages distinguished by sender (self = gradient bubble, others = dark bubble)

### 🎨 Premium Dark UI
- Dark theme with Syne + DM Sans typography
- Gradient accent colors (coral → orange)
- Animated auth screen with floating orbs
- Smooth modal animations, toast notifications
- Responsive — works on mobile (hamburger menu)
- Album art glow effect that mirrors cover color
- Volume control + seek bar

---

## 🚀 Setup

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Install ffmpeg (required for audio streaming)
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows — easiest way (PowerShell as admin):
winget install Gyan.FFmpeg
# Then restart your terminal so it's on PATH.
# OR download from https://ffmpeg.org/download.html and add bin/ to PATH
# OR set the env variable: set FFMPEG_PATH=C:\ffmpeg\bin\ffmpeg.exe
```

> **Note:** The app auto-detects ffmpeg on PATH and common install locations.
> If streaming fails, run `ffmpeg -version` in your terminal to confirm it's installed.

### 3. Run the server
```bash
python app.py
```

Visit `http://localhost:5000`

---

## 🏗️ Architecture

```
app.py                  — Flask app, REST API routes, Socket.IO events
socket_handlers.py      — WebSocket event handlers
streaming.py            — HLS audio stream management (ffmpeg)
youtube_utils.py        — YouTube/yt-dlp audio fetching
config.py               — Configuration constants

templates/
  index.html            — Single-page app shell

static/
  css/style.css         — Full design system (dark theme)
  js/auth.js            — Login/register + JWT management
  js/rooms.js           — Room create/join UI + helpers
  js/player.js          — HLS audio player
  js/socketHandler.js   — Real-time socket events
  js/main.js            — App bootstrap
```

---

## 🔒 Security Features

- **Passwords**: bcrypt hashed with salt (never stored plaintext)
- **Authentication**: JWT HS256 tokens, 7-day expiry
- **Protected API**: All room endpoints require valid JWT
- **Private rooms**: Optional password protection with bcrypt
- **XSS prevention**: All user content is escaped via `escHtml()`
- **CORS configured** for cross-origin requests

---

## 📝 Notes

- **Production**: Replace in-memory `users_db`/`music_rooms`/`chat_rooms` with a real database (PostgreSQL, MongoDB, Redis)
- **Secrets**: Set `SECRET_KEY` and `JWT_SECRET` as environment variables in production
- **HTTPS**: Deploy behind nginx with SSL for production
- **Scaling**: Use Redis adapter for Socket.IO when running multiple workers

