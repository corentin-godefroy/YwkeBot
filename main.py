from YwkeBot.database.init_database import init_database
from YwkeBot.database.video import Video

if __name__ == "__main__":
    init_database()
    Video(
        video_file_path="a",
        wiki_page_url="a",
        video_number=1,
        title="a",
        video_url="a",
        duration=1,
        description="a",
        decyphered_title="a",
        decyphered_description="a",
        info_file_path = "a"
    ).add_video()

    # with YoutubeDL(params={"windowsfilenames":True, "writeinfojson":True, "vcodec":"av01"}) as ydl:
    #     ydl.download(url_list=["https://www.youtube.com/watch?v=cTcekAXB85Q"])

    #session = login_to_fandom()
    #vids = get_last_vids()
    #create_new_pages(vids, session)
