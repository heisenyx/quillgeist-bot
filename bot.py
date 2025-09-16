import asyncio

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
from handlers.commands import *
from handlers.messages import link
from services.instagram import initialize_client
from utils.logger import setup_logger

logger = setup_logger()

commands = {
    "start": start,
    "settings": settings,
}

async def main():

    try:
        logger.info("Initializing Instagram client...")
        await asyncio.to_thread(initialize_client)
        logger.info("Instagram client initialized successfully")
    except Exception as e:
        logger.critical(f"Could not initialize Instagram client. Bot cannot start. Error: {e}")
        return

    bot = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()

    for command, handler in commands.items():
        bot.add_handler(CommandHandler(command, handler))

    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, link))

    async with bot:
        await bot.start()
        await bot.updater.start_polling()

        # Keep the bot running until it's cancelled
        await asyncio.Future()

        await bot.updater.stop()
        await bot.stop()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot process terminated by user.")