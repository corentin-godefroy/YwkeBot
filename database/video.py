from __future__ import annotations
from dataclasses import dataclass
import logging
from typing import Iterable
from YwkeBot.database.utils import LogType
from YwkeBot.database.utils import connect
from YwkeBot.database.video_logs import VideoLogs

logger = logging.getLogger(__name__)

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
                wiki_page_url TEXT NOT NULL);""")
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

    def add_video(self, user_id: int):
        """
        Insert video datas into database.
        :param user_id: user_id
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
                        wiki_page_url
                    )
                        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
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
                        self.wiki_page_url
                ))
                self.id = cursor.lastrowid
        except Exception as err:
            logger.warning(f"Video can't be added to database. Message : \"{err}\"")
            return False
        else :
            VideoLogs(log_id= None, video_id= self.id, user_id= user_id, type= LogType.CREATE, old_value= None).add_video_log()
            logger.info("Video added to database")
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