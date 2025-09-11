import yt_dlp
from telegram import InputMediaVideo
from utils.logger import setup_logger

logger = setup_logger()

ydl_opts = {
    'noplaylist': True,
    'quiet': True,
}

async def process(url: str) -> list[InputMediaVideo] | None:
    logger.info(f"Extracting info for URL: {url}")
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
        logger.error(f"Failed to process Instagram URL {url}: {e}")
        return None