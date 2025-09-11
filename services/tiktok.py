from urllib.parse import quote

import httpx
from telegram import InputMedia, InputMediaPhoto, InputMediaVideo

from services.exceptions import VideoUnavailable
from utils.logger import *

logger = setup_logger()
BASE_API_URL = f"https://douyin.wtf/api/hybrid/video_data?url="

async def process(url: str) -> None | list[InputMedia]:
    logger.info(f"Processing tiktok url: {url}")

    if "deleted" in url or "private" in url:
        raise VideoUnavailable("Video unavailable")

    safe_url = quote(url)
    api = BASE_API_URL + safe_url

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api, timeout=10)
            response.raise_for_status()
        if "application/json" not in response.headers.get("Content-Type", ""):
            logger.warning(f"Unexpected Content-Type: {response.headers.get('Content-Type')}")
            return None

        data = response.json().get("data")
        if not data:
            logger.warning("API response contained no 'data' field.")
            return None

        content_type = data.get("content_type")
        print(content_type)
        media_group = []
        match content_type:
            case "multi_photo":
                for image in data.get("image_post_info").get("images")[:10]:
                    image_url = image.get("display_image").get("url_list")[0]
                    media_group.append(InputMediaPhoto(image_url))
            case _:
                video_url = data.get("video").get("play_addr").get("url_list")[0]
                media_group.append(InputMediaVideo(video_url))
        print(media_group)
        return media_group
    except httpx.RequestError as e:
        logger.error(f"An HTTP error occurred: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None