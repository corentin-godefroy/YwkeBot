import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Informations sur le wiki et les identifiants
wiki_url = os.getenv("WIKI_URL")
username = os.getenv("CGBOT_ID")
password = os.getenv("CGBOT_PASSWORD")

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

def get_page_content(session, page_title):
    payload = {
        'action': 'query',
        'prop': 'revisions',
        'titles': page_title,
        'rvprop': 'content',
        'formatversion': '2',
        "format": "json",
    }
    page = session.get(wiki_url, params=payload)
    content = page.json()['query']['pages'][0]['revisions'][0]['content']
    return content