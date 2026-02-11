import time
import logging
import concurrent.futures
from flask_socketio import join_room, emit

from youtube_utils import fetch_song_info
from streaming import start_hls_stream, room_streams

room_queues = {}

executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

def handle_join(socketio, data):
    user = data.get('username', 'Anon')
    room = data.get('room', 'default')
    join_room(room)
    room_queues.setdefault(room, [])
    logging.info(f"{user} joined {room}")

    emit('chat', {'username': 'System', 'msg': f"{user} joined."}, room=room)

    cur = room_streams.get(room)
    if cur:
        emit('song_changed', {
            'title': cur['title'],
            'thumbnail': cur['thumbnail'],
            'duration': cur['duration']
        })
        if cur.get('status') == 'streaming':
            emit('stream_ready', {'room': room, 'timestamp': time.time()})

def handle_check_stream(data):
    room = data.get('room', 'default')
    cur = room_streams.get(room)
    if cur and cur.get('status') == 'streaming':
        emit('stream_ready', {'room': room, 'timestamp': time.time()})

def handle_chat(socketio, data):
    user = data.get('username', 'Anon')
    room = data.get('room', 'default')
    msg = data.get('msg', '').strip()

    if msg.lower().startswith('!play '):
        query = msg[6:].strip()
        if not query:
            return

        socketio.emit('chat', {'username': 'System', 'msg': f'{user} requested "{query}"'}, room=room)

        def handle_song():
            try:
                song = fetch_song_info(query)
                queue = room_queues[room]
                if room not in room_streams or room_streams[room].get('status') != 'streaming':
                    start_hls_stream(room, song, socketio)
                else:
                    queue.append(song)
                    socketio.emit('queue_updated', {'queue': [s['title'] for s in queue]}, room=room)
            except Exception as e:
                socketio.emit('chat', {'username': 'System', 'msg': f"Error: {str(e)}"}, room=room)

        executor.submit(handle_song)
        return

    if msg.lower() == '!skip':
        socketio.emit('chat', {'username': 'System', 'msg': f"{user} skipped the song"}, room=room)
        cur = room_streams.get(room)
        if cur:
            try:
                cur['ffmpeg_proc'].kill()
            except Exception as e:
                logging.error(f"Error killing ffmpeg proc: {e}")
            queue = room_queues[room]
            if queue:
                next_song = queue.pop(0)
                start_hls_stream(room, next_song, socketio)
                socketio.emit('queue_updated', {'queue': [s['title'] for s in queue]}, room=room)
            else:
                room_streams.pop(room, None)
                socketio.emit('song_stopped', {}, room=room)
        return

    socketio.emit('chat', {'username': user, 'msg': msg}, room=room)
