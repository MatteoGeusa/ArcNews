import os
import sys
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


BASE_URL = "https://arcraiders.com/it"
NEWS_URL = "https://arcraiders.com/it/news"
DB_NAME = "arc_news_database.db"


if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("ERRORE CRITICO: Token o Chat ID mancanti nel file .env")
    sys.exit(1)