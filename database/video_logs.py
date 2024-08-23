from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, tzinfo, timezone
from sqlite3 import Connection
import logging
from typing import Iterable
from database.utils import LogType, connect

logger = logging.getLogger(__name__)

def init_video_logs():
    """
    Initialise Video logs table
    """
    try:
        with connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS video_logs (
                        log_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        video_id INTEGER REFERENCES keys(id),
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        type INTEGER NOT NULL,
                        timestamp DATETIME NOT NULL,
                        old_value TEXT);""")
    except Exception as err:
        logger.error(f"Video logs table creation error: {err}")
        raise err
    else:
            logger.info("Video logs table creation successful")

@dataclass
class VideoLogs:
    log_id: int | None
    video_id: int | None
    user_id: int
    type: LogType
    old_value: str | None
    timestamp: datetime = datetime.now(timezone.utc)

    def _add_video_log(self, connection: Connection):
        try:
            connection.execute("INSERT INTO video_logs (log_id, video_id, user_id, type, old_value, timestamp) VALUES (?, ?, ?, ?, ?, ?);",
                         (self.log_id, self.video_id, self.user_id, self.type, self.old_value, self.timestamp))
        except Exception as err:
            logger.error(f"Video log insertion error: {err}")
            return False
        else:
            logger.info("Video log insertion successful")
            return True

    def add_video_log(self, connection: Connection = None) -> bool:
        """
        Add the log in the database
        :return: True if success else False
        """
        if connection is None:
            with connect() as conn:
                return self._add_video_log(conn)
        else:
            return self._add_video_log(connection)


    @classmethod
    def list_video_logs(cls) -> Iterable[VideoLogs] | None:
        """
        Recover all logs in the video logs table.
        :return: None or Iterable containing VideoLogs objects.
        """
        try:
            with connect() as conn:
                res = conn.execute("SELECT * FROM video_logs;")
        except Exception as err:
            logger.error(f"Video log consult error: {err}")
            return None
        else:
            logger.info("Video log consult successful")
            for row in res:
                yield cls(**row)

    @classmethod
    def logs_by_type(cls, type: LogType) -> Iterable[VideoLogs] | None:
        """
        Recover logs by given type in the video logs table.
        :return: None or Iterable containing VideoLogs objects.
        """
        try:
            with connect() as conn:
                res = conn.execute("SELECT * FROM video_logs WHERE type = ?;", [type])
        except Exception as err:
            logger.error(f"Getting video log by type error: {err}")
            return None
        else:
            logger.info("Getting video log by type successful")
            for row in res:
                yield cls(**row)


    @classmethod
    def logs_by_video_id(cls, video_id: int) -> Iterable[VideoLogs] | None:
        """
        Recover logs by given video id in the video logs table.
        :return: None or Iterable containing VideoLogs objects.
        """
        try:
            with connect() as conn:
                res = conn.execute("SELECT * FROM video_logs WHERE video_id = ?;", [video_id])
        except Exception as err:
            logger.error(f"Getting video log by video id error: {err}")
            return None
        else:
            logger.info("Getting video log by video id successful")
            for row in res:
                yield cls(**row)

    @classmethod
    def logs_by_user_id(cls, user_id: int) -> Iterable[VideoLogs] | None:
        """
        Recover logs by given user id in the video logs table.
        :return: None or Iterable containing VideoLogs objects.
        """
        try:
            with connect() as conn:
                res = conn.execute("SELECT * FROM video_logs WHERE user_id = ?;", [user_id])
        except Exception as err:
            logger.error(f"Getting video log by user id error: {err}")
            return None
        else:
            logger.info("Getting video log by user id successful")
            for row in res:
                yield cls(**row)

