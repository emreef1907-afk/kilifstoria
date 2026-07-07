import os

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "emre123")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

IG_API = "https://graph.instagram.com/v25.0/me/messages"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

# KilifStoria Instagram Business IDs. Echo/manual detection için kullanılır.
OWN_IDS = {
    "17841465752722469",
    "27903058482613663",
}

MAX_BOT_REPLIES_PER_USER = int(os.getenv("MAX_BOT_REPLIES_PER_USER", "5"))
MIN_SECONDS_BETWEEN_REPLIES = int(os.getenv("MIN_SECONDS_BETWEEN_REPLIES", "8"))
