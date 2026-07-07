import os

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "emre123")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

IG_API_URL = "https://graph.instagram.com/v25.0/me/messages"

# KilifStoria işletme hesabına ait olabilecek ID'ler. Echo/manüel cevap kontrolünde kullanılır.
OWN_IDS = {
    "17841465752722469",
    "27903058482613663",
}

MAX_BOT_REPLIES = int(os.getenv("MAX_BOT_REPLIES", "5"))
MIN_SECONDS_BETWEEN_REPLIES = int(os.getenv("MIN_SECONDS_BETWEEN_REPLIES", "8"))
FINAL_HANDOFF_MESSAGE = "Tasarım ve sipariş işlemi için ekip arkadaşımız birazdan size dönüş yapacak."
