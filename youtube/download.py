import os
from yt_dlp import YoutubeDL
import re
from database.utils import connect
from database.video import Video
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('YOUTUBE_API_KEY')
API_KEY_2 = os.getenv('YOUTUBE_API_KEY_2')
CHANNEL_ID = os.getenv('TRUTHSAYER_YOUTUBE_ID')

def insert_metadata_into_db(metadata):
    with connect() as conn:
        video_number = conn.execute("SELECT MAX(video_number) FROM videos").fetchone()
    wiki_page_name = re.sub(r'[#<>[\]|{}/:"?*]', '', metadata.get('title')).replace(" ", "_")
    Video(video_url= metadata.get('webpage_url'),
        video_title=metadata.get('title'),
        video_number=int(video_number) + 1,
        description=metadata.get('description'),
        duration=metadata.get('duration'),
        video_file_path=os.path.join("/mnt/HDD/HDD2/YWKE_saves/", f"{metadata.get('title')} [{metadata.get('display_id')}].webm"),
        video_info_file_path=os.path.join("/mnt/HDD/HDD2/YWKE_saves/", f"{metadata.get('title')} [{metadata.get('display_id')}].info.json"),
        wiki_page_url=f"https://youwillknoweventually.fandom.com/wiki/{wiki_page_name}",
        video_publication_date = metadata.get('timestamp')
    ).add_video(0, metadata)
    return Video



def post_process_hook(d):
    if d['status'] == 'finished' and d.get("postprocessor") == "MoveFiles":
        print(f"Téléchargement terminé pour {d['info_dict']['title']}")
        video = insert_metadata_into_db(d['info_dict'])
        #Bruteforce goes here



def download_last():
    os.makedirs('saves', exist_ok=True)
    with YoutubeDL(params={'playlistreverse': True,"postprocessor_hooks": [post_process_hook], 'restrictfilenames': True, "windowsfilenames":True, "writeinfojson":True, "vcodec":"av01", "download_archive":"var/download_archive", "paths":{"home":"/mnt/HDD/HDD2/YWKE_saves"}}) as ydl:
        ydl.download(url_list=["https://www.youtube.com/@youwillknoweventually"])




    # créer page wiki
    # bruteforce
