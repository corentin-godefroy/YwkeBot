from database.init_database import init_database
from dotenv import load_dotenv
from youtube.download import download_last
import logging
import os

load_dotenv()

if __name__ == "__main__":
    logging.basicConfig(filename=os.path.join(os.getcwd(), "var/logs"), datefmt="%a, %d %b %Y %H:%M:%S", format="%(levelname)s | %(asctime)s | %(message)s", level=logging.INFO)
    init_database()
    download_last()
