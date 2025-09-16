import asyncio
import os

import httpx
from instagrapi import Client
from instagrapi.exceptions import MediaNotFound, LoginRequired
from telegram import InputMedia, InputMediaPhoto, InputMediaVideo

from config import IG_USERNAME, IG_PASSWORD
from utils.logger import setup_logger

logger = setup_logger()

ig_client: Client | None = None

def initialize_client() -> None:
    global ig_client

    cl = Client()
    session_file = "session.json"

    try:
        if os.path.exists(session_file):
            logger.info(f"Found session file. Attempting to load.")
            session = cl.load_settings(session_file)
            cl.set_settings(session)
            cl.get_timeline_feed()
    except (LoginRequired, Exception) as e:
        logger.warning(f"Session is invalid: {e}. Need to login via username and password")
        try:
            cl.login(IG_USERNAME, IG_PASSWORD)
            logger.info("Successfully logged in via username and password.")
            cl.dump_settings(session_file)
            logger.info(f"New session saved to {os.path.abspath(session_file)}.")
        except Exception as e:
            logger.critical(f"An unexpected error occurred during login: {e}")
            raise e

    ig_client = cl

async def process(url: str) -> None | list[InputMedia]:
    logger.info(f"Processing Instagram url: {url}")

    if not ig_client:
        logger.error("Instagram client is not initialized! Cannot process link.")
        return None

    try:
        if "/share/" in url:
            logger.info(f"Resolving share link: {url}")
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, timeout=5)
            url = str(response.url)
            logger.info(f"Resolved to standard URL: {url}")

        media_id = await asyncio.to_thread(ig_client.media_pk_from_url, url)
        media_info = await asyncio.to_thread(ig_client.media_info_v1, media_id)

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