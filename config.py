import os
from dotenv import load_dotenv


load_dotenv("config.env")

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
GCS_ENGINE_ID = os.environ.get("GCS_ENGINE_ID")
GCS_API_KEY = os.environ.get("GCS_API_KEY")
MUSICXMATCH_API_KEY = os.environ.get("MUSICXMATCH_API_KEY")
GENIUS_ACCESS_TOKEN = os.environ.get('GENIUS_ACCESS_TOKEN')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID")

