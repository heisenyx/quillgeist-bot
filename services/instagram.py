import asyncio

import httpx
from instagrapi import Client
from instagrapi.exceptions import MediaNotFound
from telegram import InputMedia, InputMediaPhoto, InputMediaVideo

from config import IG_SESSION_ID
from utils.logger import setup_logger

logger = setup_logger()

_client: Client | None = None
def get_client() -> Client:
    global _client
    if _client is None:
        logger.info("Initializing and logging in Instagram client...")
        _client = Client()
        _client.login_by_sessionid(IG_SESSION_ID)
    return _client

async def process(url: str) -> None | list[InputMedia]:
    logger.info(f"Processing Instagram url: {url}")

    cl = get_client()

    try:
        if "/share/" in url:
            logger.info(f"Resolving share link: {url}")
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, timeout=5)
            url = str(response.url)
            logger.info(f"Resolved to standard URL: {url}")

        media_id = await asyncio.to_thread(cl.media_pk_from_url, url)
        media_info = await asyncio.to_thread(cl.media_info_v1, media_id)

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
    except MediaNotFound:
        logger.warning(f"No media found for url: {url}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None