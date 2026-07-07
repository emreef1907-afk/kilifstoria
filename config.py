import os
from dotenv import load_dotenv

load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "emre123")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

IG_API_URL = "https://graph.instagram.com/v25.0/me/messages"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

# Spam / güvenlik ayarları
MIN_SECONDS_BETWEEN_REPLIES = 8
MAX_SECONDS_DELAY = 15
DUPLICATE_TEXT_WINDOW_SECONDS = 45
DUPLICATE_REPLY_WINDOW_SECONDS = 120
MAX_REPLY_CHARS = 900

# Render port
PORT = int(os.getenv("PORT", "5000"))
