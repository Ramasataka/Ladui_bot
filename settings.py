import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
NEWS_API = os.getenv('NEWS_API')