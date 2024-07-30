from APIs.fandom import create_or_edit_page, update_video_page, update_chronology_page
from APIs.youtube import get_video_details


def create_new_pages(videos, session):
    for vid in videos:
        video_detail = get_video_details(vid['id']['videoId'])
        page_link = create_or_edit_page(session, video_detail)
        update_video_page(session, page_link, video_detail)
        update_chronology_page(session, page_link, video_detail)






