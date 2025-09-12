import re
from urllib.parse import urlparse

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from services import tiktok, instagram
from services.exceptions import VideoUnavailable
from utils.logger import setup_logger

logger = setup_logger()

SERVICE_HANDLERS = {
    "tiktok": tiktok.process,
    "instagram": instagram.process,
}

async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    match = re.search(r"https?://\S+", message.text)
    if not match:
        return

    video_url = match.group(0)
    handler = None

    try:
        hostname = urlparse(video_url).hostname.lower()
        if not hostname:
            return

        for service, service_handler in SERVICE_HANDLERS.items():
            if service in hostname:
                handler = service_handler
                break
    except (ValueError, IndexError):
        return

    if not handler:
        logger.error(f"Unsupported URL: {video_url}")
        await message.reply_text("Unsupported URL 😔")
        return

    try:
        await message.chat.send_chat_action(ChatAction.UPLOAD_DOCUMENT)
        media_group = await handler(video_url)

        if media_group:
            await message.reply_media_group(media=media_group)
        else:
            await message.reply_text("Could not extract any media from the link 😔")
    except VideoUnavailable:
        await message.reply_text("❌ Video unavailable")
    except Exception as e:
        logger.error(f"Unexpected error occurred {e}")