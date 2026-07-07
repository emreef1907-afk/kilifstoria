import os
from dotenv import load_dotenv

load_dotenv()

VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'emre123')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')

IG_API_URL = 'https://graph.instagram.com/v25.0/me/messages'

# Bot en fazla kaç otomatik cevap atsın?
MAX_BOT_REPLIES = int(os.getenv('MAX_BOT_REPLIES', '5'))

# Instagram aynı mesajı tekrar gönderebildiği için mid kontrolü açık.
MAX_TRACKED_MIDS = 2000
MAX_HISTORY_MESSAGES = 10

# Render için port
PORT = int(os.getenv('PORT', '5000'))
