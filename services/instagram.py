from instagrapi import Client
from telegram import InputMedia, InputMediaPhoto, InputMediaVideo

from config import IG_SESSION_ID
from utils.logger import setup_logger

logger = setup_logger()

cl = Client()
cl.login_by_sessionid(IG_SESSION_ID)

async def process(url: str) -> None | list[InputMedia]:
    logger.info(f"Processing Instagram url: {url}")

    try:
        media_id = cl.media_pk_from_url(url)
        media_info = cl.media_info_v1(media_id)
        if not media_info:
            logger.warning(f"No media found for url: {url}")
            return None

        media_type = media_info.media_type

        media_group = []
        match media_type:
            case 1:
                media_group.append(InputMediaPhoto(str(media_info.thumbnail_url)))
            case 2:
                media_group.append(InputMediaVideo(str(media_info.video_url)))
            case 8:
                for media in media_info.resources[:10]:
                    if media.media_type == 1:
                        media_group.append(InputMediaPhoto(str(media.thumbnail_url)))
                    else:
                        media_group.append(InputMediaVideo(str(media.video_url)))
        return media_group

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None