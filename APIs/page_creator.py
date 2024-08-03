from APIs.fandom import create_or_edit_page, update_video_page, update_chronology_page, create_redirection_page, \
    get_next_video_number
from APIs.youtube import get_video_details


def create_new_pages(videos, session):
    for vid in videos:
        video_detail = get_video_details(vid['id']['videoId'])
        page_link = create_or_edit_page(session, video_detail)
        video_number = update_video_page(session, page_link, video_detail)
        update_chronology_page(session, page_link, video_detail)
        page_name = page_link.split('/')[-1]
        create_redirection_page(session, video_number, page_name)







