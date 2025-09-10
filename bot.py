from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
from handlers.commands import *
from handlers.messages import link
from utils.logger import setup_logger

logger = setup_logger()

commands = {
    "start": start,
    "settings": settings,
}

def main():
    bot = Application.builder().token(BOT_TOKEN).build()

    for command, handler in commands.items():
        bot.add_handler(CommandHandler(command, handler))

    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, link))

    bot.run_polling()

if __name__ == '__main__':
    main()
