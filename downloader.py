import yt_dlp


def download(url, newdirection=''):
    options = {
        'format': 'bestaudio/best',
        'exractaudio': True,
        'audioformat': "mp3",
        'outtmpl': f'{newdirection}/mus1_/%(title)s.%(ext)s',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    audio_downloader = yt_dlp.YoutubeDL(options)
    audio_downloader.extract_info(url)
    #filename = audio_downloader.prepare_filename(info)
    #download.filename = filename[filename.rfind('\\') + 1:-5]



