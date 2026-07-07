import os
from dotenv import load_dotenv

load_dotenv()

VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'emre123')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')
IG_API = 'https://graph.instagram.com/v25.0/me/messages'
MAX_BOT_REPLIES = 5
MIN_SECONDS_BETWEEN_REPLIES = 6
DUPLICATE_INCOMING_WINDOW = 45
DUPLICATE_REPLY_WINDOW = 120
HANDOFF_MESSAGE = 'Tasarım ve sipariş işlemi için ekip arkadaşımız birazdan size dönüş yapacak.'
