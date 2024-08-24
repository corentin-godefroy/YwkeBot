from __future__ import annotations
import os
import re
from dataclasses import dataclass
import logging
from datetime import datetime
from typing import Iterable

from bruteforce.bruteforce import bruteforce
from database.utils import LogType
from database.utils import connect
from database.video_logs import VideoLogs
from fandom.utils import login_to_fandom, get_page_content
from dotenv import load_dotenv
from fandom.upload_file import upload_file
from youtube.download_thumbnail import thumbnail_downloader

logger = logging.getLogger(__name__)

load_dotenv()

wiki_url = os.getenv("WIKI_URL")
username = os.getenv("CGBOT_ID")
password = os.getenv("CGBOT_PASSWORD")


def init_video():
    """
    Initialise video table.
    :return:
    """
    try:
        with connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                video_file_path TEXT NOT NULL,
                video_info_file_path TEXT NOT NULL,
                video_url TEXT NOT NULL,
                video_number INTEGER NOT NULL,
                video_title TEXT NOT NULL,
                decyphered_title TEXT,
                description TEXT,
                decyphered_description TEXT,
                duration INTEGER NOT NULL,
                wiki_page_url TEXT NOT NULL,
                video_publication_date INTEGER NOT NULL);""")
    except Exception as err:
        logger.error(f"Video table creation error: {err}")
        raise err
    else:
        logger.info("Video table creation successful")


@dataclass
class Video:
    video_file_path: str
    video_info_file_path: str
    video_url: str
    video_publication_date: int
    video_number: int
    video_title: str
    description: str
    duration: int
    wiki_page_url: str
    decyphered_title: str = ""
    decyphered_description: str = ""
    id: int | None = None

    def __post_init__(self):
        if self.video_info_file_path is None:
            logger.warning("Video file path cannot be None")
        if self.video_file_path is None:
            logger.warning("Video file can't hasn't be downloaded")
        if self.wiki_page_url is None:
            raise ValueError("Video wiki_page_url cannot be None")
        if self.video_number is None:
            raise ValueError("Video number cannot be None")
        if self.video_title is None:
            raise ValueError("Video title cannot be None")
        if self.video_url is None:
            raise ValueError("Video url cannot be None")
        if self.duration is None:
            raise ValueError("Video duration cannot be None")

    def _create_new_video_page(self, metadata, session):
        (thumbnail_path, file_name) = thumbnail_downloader(metadata)
        miniature_path = upload_file(thumbnail_path, file_name)

        with connect() as conn:
            video_number = conn.execute("SELECT video_number FROM videos WHERE video_title = ?",
                                        [self.video_title]).fetchone()

        if str(video_number['video_number']).endswith("1"):
            video_number = str(video_number['video_number']) + "st"
        elif str(video_number['video_number']).endswith("2"):
            video_number = str(video_number['video_number']) + "nd"
        elif str(video_number['video_number']).endswith("3"):
            video_number = str(video_number['video_number']) + "rd"
        else:
            video_number = str(video_number['video_number']) + "th"

        description = metadata.get('description')
        original_title = metadata.get('title')
        page_title = re.sub(r'[#<>[\]|{}/:"?*]', '', original_title)
        page_title.replace(" ", "_")

        decoded_title = "''Not decyphered yet''"
        decoded_description = "''Not decyphered yet''"
        publication_date = datetime.fromtimestamp(self.video_publication_date).strftime("%B %d %Y %H:%M:%S")
        duration = metadata.get('duration_string')
        cypher = "''Not found yet''"
        cypher_2 = "''Not found yet''"
        music_style = "''Undefined''"

        link = metadata.get('webpage_url')
        infobox_title = decoded_title
        miniature = f"File:{miniature_path}"
        try:
            caption_miniature = re.findall(r'- image credit -\n(.*)', description)[0]
        except:
            caption_miniature = ""

        timestamps = re.findall(r'(\d{2}:\d{2}) - (.*)', description)
        transformed_timestamps = []
        for i in range(len(timestamps)):
            start_time = timestamps[i][0]
            title = timestamps[i][1]
            end_time = timestamps[i + 1][0] if i + 1 < len(timestamps) else duration
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
        template = template.replace("{{duration}}", duration)
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
        template = template.replace("{{cypher}}", cypher)
        template = template.replace("{{decoded_description}}", decoded_description)
        template = template.replace("{{cypher_2}}", cypher_2)

        # Payload pour la création/modification de la page
        edit_payload = {
            'action': 'edit',
            'meta': 'tokens',
            'format': 'json',
            'title': page_title,
            'text': template,
            'token': session.csrf_token,
            'createonly': 'true'
        }
        response = session.post(wiki_url, data=edit_payload)
        response_data = response.json()

        if 'error' in response_data:
            if not response_data['error']['code'] == 'articleexists':
                raise Exception(f"Error creating/editing page: {response_data['error']['info']}")

        print(f"Page '{page_title}' créée avec succès.")
        return page_title

    def _update_chronology(self, session):
        publication_date = datetime.fromtimestamp(self.video_publication_date).strftime("%B %d %Y %H:%M:%S")

        content = get_page_content(session, 'Chronology')

        content = content[:-2]

        last_number = self.video_number

        # add last video page link
        content += f"|-\n| {last_number} || {publication_date} || [[{self.wiki_page_url.split("/")[-1]}]]\n|}}"

        payload = {
            'action': 'edit',
            'title': 'Chronology',
            'text': content,
            'token': session.csrf_token,
            'format': 'json'
        }
        session.post(wiki_url, data=payload)

    def _update_videos(self, session):
        publication_date = datetime.fromtimestamp(self.video_publication_date).strftime("%B %d %Y %H:%M:%S")
        # get the wikicode of this page https://youwillknoweventualy.fandom.com/wiki/Category:Vid%C3%A9o for editing code

        content = get_page_content(session, 'Category:Vidéo')
        last_number = self.video_number

        content = content[:-2]

        # add last video page link
        content += f"|-\n| {last_number} || {publication_date} || [[{self.wiki_page_url.split("/")[-1]}]]\n|}}"

        payload = {
            'action': 'edit',
            'title': 'Category:Vidéo',
            'text': content,
            'token': session.csrf_token,
            'format': 'json'
        }
        response = session.post(wiki_url, data=payload)
        return last_number

    def update_fandom(self, metadata, session):
        self._create_new_video_page(metadata, session)
        self._update_videos(session)
        self._update_chronology(session)

    def add_video(self, user_id: int, metadata):
        """
        Insert video datas into database.
        :param user_id: user_id
        :param metadata: metadata of the video
        :return: True if succeed else False.
        """
        try:
            with connect() as conn:
                cursor = conn.execute(
                    """INSERT INTO videos (
                        id,
                        video_file_path,
                        video_info_file_path,
                        video_url,
                        video_number,
                        video_title,
                        decyphered_title,
                        description,
                        decyphered_description,
                        duration,
                        wiki_page_url,
                        video_publication_date
                    )
                        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        self.video_file_path,
                        self.video_info_file_path,
                        self.video_url,
                        self.video_number,
                        self.video_title,
                        self.decyphered_title,
                        self.description,
                        self.decyphered_description,
                        self.duration,
                        self.wiki_page_url,
                        self.video_publication_date
                ))
                self.id = cursor.lastrowid
        except Exception as err:
            logger.warning(f"Video can't be added to database. Message : \"{err}\"")
            return False
        else :
            VideoLogs(log_id= None, video_id= self.id, user_id= user_id, type= LogType.CREATE, old_value= None).add_video_log()
            logger.info("Video added to database")
            session = login_to_fandom()
            self.update_fandom(metadata, session)
            return True

    @classmethod
    def get_video(cls, video_id: int, user_id: int) -> Video | None:
        """
        Recover video's datas in the database by given id.
        :param cls: Video's class
        :param video_id: Video's id to find in database
        :param user_id: User's id that make the research
        :return: Video object with data
        """
        try:
            with connect() as conn:
                data = conn.execute("SELECT * FROM videos WHERE id = ?;", [video_id]).fetchone()
        except Exception as err:
            logger.error(f"Video not found. Message: '{err}")
            return None
        else:
            VideoLogs(log_id=None, video_id=None, user_id=user_id, type=LogType.READ, old_value=None).add_video_log()
            logger.info(f"Video found with id: {video_id}")
            return cls(**data)

    @classmethod
    def list_videos(cls, user_id: int)-> Iterable[Video] | None:
        """
        List all videos.
        :param user_id: User's id that make the research.
        :return: iterable of videos
        """
        try:
            with connect() as conn:
                res = conn.execute("SELECT * FROM videos;")
        except Exception as err:
            logger.error(f"No video found. Message: {err}")
            return None
        else:
            VideoLogs(log_id=None, video_id=None, user_id=user_id, type=LogType.READ, old_value=None).add_video_log()
            for video in res:
                yield cls(**video)

    def modify_video(self, user_id: int) -> bool:
        """
        Save modified object in the database.
        :param user_id: User's id that make the research.
        :return: True if succeed else False.
        """
        try:
            with connect() as conn:
                old = conn.execute("SELECT * FROM videos WHERE id = ?;", [self.id]).fetchone()
                conn.execute(
                    """UPDATE videos SET 
                    video_file_path = ?,
                    video_info_file_path = ?,
                    video_url = ?,
                    video_number = ?,
                    video_title = ?,
                    decyphered_title = ?,
                    description = ?,
                    decyphered_description = ?,
                    duration = ?,
                    wiki_page_url = ?
                    WHERE id = ?;""",
                    [
                        self.video_file_path,
                        self.video_info_file_path,
                        self.video_url,
                        self.video_number,
                        self.video_title,
                        self.decyphered_title,
                        self.description,
                        self.decyphered_description,
                        self.duration,
                        self.wiki_page_url,
                        self.id
                    ]
                )
        except Exception as err:
            logger.error(f"Video can't be updated in database. Message : \"{err}\"")
            return False
        else:
            VideoLogs(log_id=None, video_id=self.id, user_id=user_id, type=LogType.MODIFY, old_value=str(old)).add_video_log()
            logger.info("Video updated in database")
            return True

    def delete_video(self, user_id: int) -> bool:
        """
        Delete video data in the database.
        :param user_id: User's id that make the research.
        :return: True if succeed else False.
        """

        try:
            with connect() as conn:
                old = conn.execute("SELECT * FROM videos WHERE id = ?;", [self.id]).fetchone()
                conn.execute("DELETE FROM videos WHERE id = ?", [self.id])
        except Exception as err:
            logger.error(f"Video can't be deleted in database. Message : \"{err}\"")
            return False
        else:
            VideoLogs(log_id=None, video_id=self.id, user_id=user_id, type=LogType.DELETE, old_value=str(old)).add_video_log()
            logger.info("Video deleted in database")
            return True

    def bruteforce(self):
        bruteforce(self)