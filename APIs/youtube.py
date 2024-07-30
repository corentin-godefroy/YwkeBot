import json
import os
import requests
import re

API_KEY = os.environ.get('YOUTUBE_API_KEY')
API_KEY_2 = os.environ.get('YOUTUBE_API_KEY_2')
CHANNEL_ID = os.environ.get('THRUTHSAYER_YOUTUBE_ID')

def get_latest_videos(max_results=5):
    if max_results != 0:
        url = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={CHANNEL_ID}&part=id&order=date&maxResults={max_results}"
        response = requests.get(url)
        if response.status_code == 403:
            url = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY_2}&channelId={CHANNEL_ID}&part=id&order=date&maxResults={max_results}"
            response = requests.get(url)
        videos = response.json().get('items', [])
        videos.reverse()
        return videos
    else:
        print("No new videos detected")
        return []


def get_video_details(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?key={API_KEY}&part=snippet&id={video_id}"
    response = requests.get(url)
    if response.status_code == 403:
        url = f"https://www.googleapis.com/youtube/v3/videos?key={API_KEY_2}&part=snippet&id={video_id}"
        response = requests.get(url)
    video_details = response.json().get('items', [])[0]
    a = json.dumps(video_details)
    return video_details

def get_video_duration(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=contentDetails&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 403:
        url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=contentDetails&key={API_KEY_2}"
        response = requests.get(url)
    video_duration = response.json().get('items', [])[0]['contentDetails']['duration']
    return video_duration

def get_channel_number_vids():
    url = f"https://www.googleapis.com/youtube/v3/channels?key={API_KEY}&id={CHANNEL_ID}&part=statistics"
    response = requests.get(url)
    if response.status_code == 403:
        url = f"https://www.googleapis.com/youtube/v3/channels?key={API_KEY_2}&id={CHANNEL_ID}&part=statistics"
        response = requests.get(url)

    channel_statistics = response.json().get('items', [])[0]['statistics']['videoCount']
    return channel_statistics

def get_last_vids():
    number_of_vids = get_channel_number_vids()

    with open("last_number_of_videos.txt", 'r+') as file:
        last_videos = int(file.read())
        file.seek(0)
        file.write(number_of_vids)
        file.truncate()

    n_lasts = int(number_of_vids) - int(last_videos)

    return get_latest_videos(n_lasts)

def miniature_downloader(video):
    tumbnail = video['snippet']['thumbnails']['maxres']['url']
    title = video['snippet']['title']
    title = re.sub(r'[#<>[\]|{}]', '', title)
    miniature = requests.get(tumbnail)
    with open(f"{title}.jpg", 'wb') as file:
        file.write(miniature.content)

    return f"{title}.jpg"


