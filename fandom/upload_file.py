import os
from dotenv import load_dotenv
from fandom.utils import login_to_fandom

load_dotenv()

# Informations sur le wiki et les identifiants
wiki_url = os.getenv("WIKI_URL")
username = os.getenv("CGBOT_ID")
password = os.getenv("CGBOT_PASSWORD")


def upload_file(file_path, file_name):
    # Post request to upload a file from a URL
    with login_to_fandom() as session:
        PARAMS = {
            "action": "upload",
            "filename": f"{file_path}",
            "format": "json",
            "ignorewarnings": 1,
            "token": session.csrf_token,
        }

        with open(file_path, 'rb') as file:
            response = session.post(wiki_url, data=PARAMS, files={'file': (file_path, file, 'multipart/form-data')})
        filename = ""
        try:
            if response.json()['upload']['result'] == 'Success':
                print(f"File '{file_name}' uploaded successfully.")
                filename = response.json()['upload']['filename']
        except KeyError:
            print(f"Error uploading file: {response.json()['error']['info']}")
            if response.json()['error']['code'] == 'fileexists-forbidden':
                filename = response.json()['error']['info'].split(' ')[-1].split(':')[1].split('|')[0]
        os.remove(file_path)
        return filename