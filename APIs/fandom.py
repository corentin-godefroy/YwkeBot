import os
import isodate
import requests
from datetime import datetime
import re
from APIs.youtube import get_video_duration, miniature_downloader

# Informations sur le wiki et les identifiants
wiki_url = os.environ.get("WIKI_URL")
username = os.environ.get("CGBOT_ID")
password = os.environ.get("CGBOT_PASSWORD")


def login_to_fandom():
    # Créer une session
    session = requests.Session()
    # URL pour se connecter
    payload = {
        'action': 'query',
        'meta': 'tokens',
        'format': 'json',
        'type': 'login'
    }
    res = session.get(wiki_url, params=payload)
    token = res.json()['query']['tokens']['logintoken']

    # Payload pour la connexion
    login_payload = {
        'action': 'login',
        'format': 'json',
        'lgname': username,
        'lgpassword': password,
        'lgtoken': token,
    }

    # Se connecter
    response = session.post(wiki_url, data=login_payload)
    response_data = response.json()

    payload = {
        'action': 'query',
        'meta': 'tokens',
        'type': 'csrf',
        'format': 'json'
    }

    res = session.get(wiki_url, params=payload)
    session.csrf_token = res.json()['query']['tokens']['csrftoken']

    if res.status_code != 200:
        raise Exception(f"Error logging in: {response_data['error']['info']}")

    print("Connecté avec succès.")
    return session


def create_or_edit_page(session, video_detail):
    miniature_path = miniature_downloader(video_detail)
    file_name = re.sub(r'[#<>[\]|{}]', '', video_detail['snippet']['title'])
    miniature_path = upload_file(session, miniature_path, file_name)

    description = video_detail['snippet']['description']
    page_title = video_detail['snippet']['title']
    page_title = re.sub(r'[#<>[\]|{}]', '', page_title)
    original_title = page_title
    decoded_title = "''Not decyphered yet''"
    decoded_description = "''Not decyphered yet''"
    publication_date = datetime.strptime(video_detail['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ").strftime(
        "%B %d %y %H:%M:%S")
    duration = get_video_duration(video_detail['id'])
    try:
        duration = isodate.parse_duration(duration)
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        video_duration = f"{hours}h {minutes}m {seconds}s"
        if hours == 0:
            final_time = f"{minutes:02}:{seconds:02}"
        else:
            final_time = f"{hours:02}:{minutes:02}:{seconds:02}"
    except:
        video_duration = " "
    link = f"https://www.youtube.com/watch?v={video_detail['id']}"
    infobox_title = "''Not decyphered yet''"
    miniature = f"File:{miniature_path}"
    try:
        caption_miniature = re.findall(r'- image credit -\n(.*)', description)[0]
    except:
        caption_miniature = ""
    video_number = "nth"
    cypher = "''Not found yet''"
    music_style = "''Undefined''"

    timestamps = re.findall(r'(\d{2}:\d{2}) - (.*)', description)
    transformed_timestamps = []
    for i in range(len(timestamps)):
        start_time = timestamps[i][0]
        title = timestamps[i][1]
        end_time = timestamps[i + 1][0] if i + 1 < len(timestamps) else final_time
        transformed_timestamps.append(f"#{start_time}-{end_time} {title}")

    chapters_count = len(transformed_timestamps)
    # Reconcaténation en un unique paragraphe avec des retours à la ligne
    chapters = '\n'.join(transformed_timestamps)
    end_marker = '- timestamps -'
    end_index = description.find(end_marker)
    encoded_description = ''

    if end_index != -1:
        encoded_description = description[:end_index].strip()

    with open("templates/video_page", "r") as file:
        template = file.read()

    # Remplacement des variables du modèle
    template = template.replace("{{title}}", original_title)
    template = template.replace("{{decoded_title}}", decoded_title)
    template = template.replace("{{publication_date}}", publication_date)
    template = template.replace("{{duration}}", video_duration)
    template = template.replace("{{link}}", link)
    template = template.replace("{{infobox_title}}", infobox_title)
    template = template.replace("{{File:filename}}", miniature)
    template = template.replace("{{caption-miniature}}", caption_miniature)
    template = template.replace("{{video_number}}", video_number)
    template = template.replace("{{chapters}}", chapters)
    template = template.replace("{{chapters_count}}", str(chapters_count))
    template = template.replace("{{music_style}}", music_style)
    template = template.replace("{{encoded_description}}", encoded_description)
    template = template.replace("{{original_title}}", original_title)
    template = template.replace("{{date}}", publication_date)
    template = template.replace("{{duration}}", video_duration)
    template = template.replace("{{cypher}}", cypher)
    template = template.replace("{{decoded_description}}", decoded_description)

    # Payload pour la création/modification de la page
    edit_payload = {
        'action': 'edit',
        'meta': 'tokens',
        'format': 'json',
        'title': page_title,
        'text': template,
        'token': session.csrf_token,
    }
    response = session.post(wiki_url, data=edit_payload)
    response_data = response.json()

    if 'error' in response_data:
        raise Exception(f"Error creating/editing page: {response_data['error']['info']}")

    print(f"Page '{page_title}' créée/modifiée avec succès.")
    return page_title


def upload_file(session, file_path, file_name):
    # Step 4: Post request to upload a file from a URL
    PARAMS_4 = {
        "action": "upload",
        "filename": f"{file_path}",
        "format": "json",
        "ignorewarnings": 1,
        "token": session.csrf_token,
    }

    with open(file_path, 'rb') as file:
        file = {'file': (file_path, file, 'multipart/form-data')}
        response = session.post(wiki_url, data=PARAMS_4, files=file)

    try:
        if response.json()['upload']['result'] == 'Success':
            print(f"File '{file_name}' uploaded successfully.")
            os.remove(file_path)
            return response.json()['upload']['filename']
    except KeyError:
        print(f"Error uploading file: {response.json()['error']['info']}")
        if response.json()['error']['code'] == 'fileexists-forbidden':
            filename = response.json()['error']['info'].split(' ')[-1].split(':')[1].split('|')[0]
            os.remove(file_path)
            return filename


def update_video_page(session, page_link, video_detail):
    publication_date = datetime.strptime(video_detail['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ").strftime(
        "%B %d %y %H:%M:%S")
    #get the wikicode of this page https://youwillknoweventualy.fandom.com/wiki/Category:Vid%C3%A9o for editing code

    payload = {
        'action': 'query',
        'prop': 'revisions',
        'titles': 'Category:Vidéo',
        'rvprop': 'content',
        'formatversion': '2',
        "format": "json",
    }
    page = session.get(wiki_url, params=payload)
    content = page.json()['query']['pages'][0]['revisions'][0]['content']
    # remove last |}
    content = content[:-2]

    last_number = re.findall(r'\|-(\n\| \d+)', content)[-1]
    last_number = last_number.split(' ')[1]
    last_number = int(last_number) + 1

    # add last video page link
    content += f"|-\n| {last_number} || {publication_date} || [[{page_link}]]\n|}}"

    payload = {
        'action': 'edit',
        'title': 'Category:Vidéo',
        'text': content,
        'token': session.csrf_token,
        'format': 'json'
    }
    response = session.post(wiki_url, data=payload)


def update_chronology_page(session, page_link, video_detail):
    publication_date = datetime.strptime(video_detail['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ").strftime(
        "%B %d %y %H:%M:%S")

    payload = {
        'action': 'query',
        'prop': 'revisions',
        'titles': 'Chronology',
        'rvprop': 'content',
        'formatversion': '2',
        "format": "json",
    }
    page = session.get(wiki_url, params=payload)
    content = page.json()['query']['pages'][0]['revisions'][0]['content']
    # remove last |}
    content = content[:-2]

    last_number = re.findall(r'\|-(\n\| \d+)', content)[-1]
    last_number = last_number.split(' ')[1]
    last_number = int(last_number) + 1

    # add last video page link
    content += f"|-\n| {last_number} || {publication_date} || [[{page_link}]]\n|}}"

    payload = {
        'action': 'edit',
        'title': 'Chronology',
        'text': content,
        'token': session.csrf_token,
        'format': 'json'
    }
    session.post(wiki_url, data=payload)


def create_redirection_page(session, video_number, redirection_title):
    if str(video_number).endswith("1"):
        th = "st"
    elif str(video_number).endswith("2"):
        th = "nd"
    elif str(video_number).endswith("3"):
        th = "rd"
    else:
        th = "th"

    payload = {
        'action': 'edit',
        'title': f"{video_number}{th} video",
        'text': f"#redirect [[{redirection_title}]]",
        'token': session.csrf_token,
        'format': 'json',
    }
    response = session.post(wiki_url, data=payload)
    response_data = response.json()

    if 'error' in response_data:
        raise Exception(f"Error creating redirection page: {response_data['error']['info']}")
