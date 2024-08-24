import os.path
import re
import requests
from PIL import Image


def thumbnail_downloader(d):
    thumbnail_url = d.get('thumbnail')
    title = d.get('title')
    title = re.sub(r'[#<>[\]|{}/:"?*]', '_', title)
    miniature = requests.get(thumbnail_url)
    path = os.path.join(os.getcwd(), f"var/{title}.jpg")
    with open(path, 'wb') as file:
        file.write(miniature.content)

    image = Image.open(path)
    image = image.convert('RGB')
    path2 = os.path.join(os.getcwd(), f"var/{title}.webp")
    image.save(path2, 'webp')

    os.remove(path)

    return (path2, title)