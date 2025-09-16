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

def main():

    try:
        logger.info("Initializing Instagram client...")
        initialize_client()
    except Exception as e:
        logger.critical(f"FATAL: Could not initialize Instagram client. Bot cannot start. Error: {e}")
        return

    bot = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()

    for command, handler in commands.items():
        bot.add_handler(CommandHandler(command, handler))

    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, link))

    bot.run_polling()

if __name__ == '__main__':
    main()
