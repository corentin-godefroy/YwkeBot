import os
from yt_dlp import YoutubeDL

def download_last():
    os.makedirs('saves', exist_ok=True)
    with YoutubeDL(params={"windowsfilenames":True, "writeinfojson":True, "vcodec":"av01", "download_archive":"var/download_archive", "paths":{"home":"saves"}}) as ydl:
        ydl.download(url_list=["https://www.youtube.com/@youwillknoweventually"])
    # créer page wiki
    # créer input database
    # bruteforce
