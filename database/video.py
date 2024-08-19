import os
from dataclasses import dataclass
from sqlite3 import Connection
import logging

logger = logging.getLogger(__name__)

def init_video():
    with Connection(database="./ywke_database") as conn:
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

@dataclass
class Video:
    info_file_path: str
    video_file_path: str
    wiki_page_url: str
    video_url: str
    video_number: int
    title: str
    duration: int
    description: str = ""
    decyphered_title: str | None = None
    decyphered_description: str | None = None

    def __post_init__(self):
        if self.info_file_path is None:
            logger.warning("Video file path cannot be None")
        if self.video_file_path is None:
            logger.warning("Video file can't hasn't be downloaded")
        if self.wiki_page_url is None:
            raise ValueError("Video wiki_page_url cannot be None")
        if self.video_number is None:
            raise ValueError("Video number cannot be None")
        if self.title is None:
            raise ValueError("Video title cannot be None")
        if self.video_url is None:
            raise ValueError("Video url cannot be None")
        if self.duration is None:
            raise ValueError("Video duration cannot be None")



    def add_video(self):
        logging.basicConfig(filename=os.path.join(os.getcwd(), "logs"), level=logging.INFO)
        with Connection(database=os.path.join(os.getcwd(), "ywke_database")) as conn:
            try:
                conn.execute(
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
                        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        self.video_file_path,
                        self.info_file_path,
                        self.video_url,
                        self.video_number,
                        self.title,
                        self.decyphered_title,
                        self.description,
                        self.decyphered_description,
                        self.duration,
                        self.wiki_page_url
                ))
            except Exception as err:
                print(self.video_url)
                logger.warning(f"Video can't be added to database. Message : \"{err}\"")
            else :
                logger.info("Video added to database")

