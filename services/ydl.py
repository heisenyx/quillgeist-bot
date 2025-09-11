import os
import tempfile

import yt_dlp
from telegram import InputMediaVideo

from config import YDL_COOKIES
from utils.logger import setup_logger

logger = setup_logger()

def get_ydl_opts():
    opts = {
        'noplaylist': True,
        'quiet': True,
    }

    if YDL_COOKIES:
        temp_cookie_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8')
        temp_cookie_file.write(YDL_COOKIES)
        temp_cookie_file.close()

        opts['cookiefile'] = temp_cookie_file.name
        logger.info("Using cookies from env variable")
        return opts, temp_cookie_file.name

    logger.warning("YDL_COOKIES environment variable not set. Proceeding without authentication")
    return opts, None

async def process(url: str) -> list[InputMediaVideo] | None:
    logger.info(f"Extracting info for URL: {url}")

    ydl_opts, temp_cookie_path = get_ydl_opts()
    direct_url = None

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            for f in reversed(info['formats']):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                    logger.info(f"Found suitable pre-merged format: {f.get('format_id')} at {f.get('height')}p")
                    direct_url = f['url']
                    break

            if direct_url:
                return [InputMediaVideo(media=direct_url)]
            else:
                logger.warning("No pre-merged video format found for this URL")
                return None

    except Exception as e:
        logger.error(f"Failed to process URL {url}: {e}")
        return None
    finally:
        if temp_cookie_path and os.path.exists(temp_cookie_path):
            os.remove(temp_cookie_path)
            logger.info(f"Cleaned up temporary cookie file: {temp_cookie_path}")