import yt_dlp

def fetch_song_info(query):
    opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'extractor_retries': 1,
        'socket_timeout': 5,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
    return {
        'url': info['url'],
        'title': info.get('title', 'Unknown'),
        'thumbnail': info.get('thumbnail', ''),
        'duration': info.get('duration', 0)
    }
