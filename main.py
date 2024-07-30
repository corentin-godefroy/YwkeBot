from APIs.fandom import login_to_fandom, update_video_page
from APIs.page_creator import create_new_pages
from APIs.youtube import get_last_vids

if __name__ == "__main__":
    session = login_to_fandom()
    vids = get_last_vids()
    create_new_pages(vids, session)
