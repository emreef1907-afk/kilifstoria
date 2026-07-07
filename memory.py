import time
from config import MAX_BOT_REPLIES, DUPLICATE_INCOMING_WINDOW, DUPLICATE_REPLY_WINDOW

users = {}
processed_mids = set()
bot_sent_mids = set()
recent_incoming = {}
recent_replies = {}


def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            'history': [],
            'handoff': False,
            'model': False,
            'design': False,
            'photo': False,
            'asked_more_questions': False,
            'bot_replies': 0,
            'last_reply_time': 0,
        }
    return users[user_id]


def remember_incoming(user_id, text):
    key = (user_id, (text or '').strip().lower())
    now = time.time()
    last = recent_incoming.get(key, 0)
    if now - last < DUPLICATE_INCOMING_WINDOW:
        return False
    recent_incoming[key] = now
    return True


def remember_reply(user_id, reply):
    key = (user_id, (reply or '').strip().lower())
    now = time.time()
    last = recent_replies.get(key, 0)
    if now - last < DUPLICATE_REPLY_WINDOW:
        return False
    recent_replies[key] = now
    return True


def can_bot_continue(user_id):
    user = get_user(user_id)
    return not user['handoff'] and user['bot_replies'] < MAX_BOT_REPLIES


def mark_handoff(user_id):
    get_user(user_id)['handoff'] = True
