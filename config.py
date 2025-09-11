import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

YDL_COOKIES = os.getenv('YDL_COOKIES')