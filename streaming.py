import os
import time
import subprocess
import logging

from config import HLS_ROOT, FFMPEG_PATH

room_streams = {}


def start_hls_stream(room, song, socketio):
    hls_dir = os.path.join(HLS_ROOT, room)
    os.makedirs(hls_dir, exist_ok=True)

    room_streams[room] = {
        'title': song['title'],
        'thumbnail': song['thumbnail'],
        'duration': song['duration'],
        'status': 'preparing'
    }

    for f in os.listdir(hls_dir):
        try:
            os.remove(os.path.join(hls_dir, f))
        except Exception as e:
            logging.error(f"Error removing file {f}: {e}")

    old_proc = room_streams.get(room, {}).get('ffmpeg_proc')
    if old_proc:
        try:
            old_proc.kill()
            time.sleep(0.5)
        except Exception as e:
            logging.error(f"Error killing ffmpeg: {e}")

    socketio.emit('song_changed', {
        'title': song['title'],
        'thumbnail': song['thumbnail'],
        'duration': song['duration']
    }, room=room)

    cmd = [
        FFMPEG_PATH, '-re', '-i', song['url'],
        '-c:a', 'aac', '-b:a', '192k', '-f', 'hls',
        '-hls_time', '2', '-hls_list_size', '5',
        '-hls_flags', 'delete_segments+append_list',
        '-hls_segment_filename', os.path.join(hls_dir, 'segment_%d.ts'),
        os.path.join(hls_dir, 'stream.m3u8')
    ]

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        room_streams[room]['ffmpeg_proc'] = proc

        # Wait briefly to give FFmpeg time to start and create stream files
        timeout_seconds = 10
        poll_interval = 0.5
        elapsed = 0
        while elapsed < timeout_seconds:
            if os.path.exists(os.path.join(hls_dir, 'stream.m3u8')):
                break
            if proc.poll() is not None:
                logging.error("FFmpeg exited prematurely.")
                room_streams[room]['status'] = 'error'
                socketio.emit('chat', {'username': 'System', 'msg': "Error playing the song."}, room=room)
                return False
            time.sleep(poll_interval)
            elapsed += poll_interval

        if not os.path.exists(os.path.join(hls_dir, 'stream.m3u8')):
            logging.error("Stream file not created in time.")
            room_streams[room]['status'] = 'error'
            socketio.emit('chat', {'username': 'System', 'msg': "Error: Stream could not start."}, room=room)
            return False

        room_streams[room]['status'] = 'streaming'
        socketio.emit('stream_ready', {'room': room, 'timestamp': time.time()}, room=room)
        return True

    except Exception as e:
        logging.error(f"Stream error: {e}")
        room_streams[room]['status'] = 'error'
        socketio.emit('chat', {'username': 'System', 'msg': f"Error: {str(e)}"}, room=room)
        return False
