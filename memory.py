import time
from collections import deque
from config import MAX_BOT_REPLIES_PER_USER

USERS = {}
PROCESSED_MIDS = set()
BOT_SENT_MIDS = set()
PROCESSING_USERS = set()

# Basit temizlik için sınır. Render restart olursa zaten bellek sıfırlanır.
MAX_PROCESSED = 3000


def get_user(user_id: str):
    if user_id not in USERS:
        USERS[user_id] = {
            "history": [],
            "handoff": False,
            "model": False,
            "design": False,
            "photo": False,
            "bot_replies": 0,
            "last_reply_time": 0,
            "created_at": time.time(),
        }
    return USERS[user_id]


def remember_mid(mid: str) -> bool:
    """True dönerse mesaj yeni; False dönerse daha önce işlenmiş."""
    if not mid:
        return True
    if mid in PROCESSED_MIDS:
        return False
    PROCESSED_MIDS.add(mid)
    if len(PROCESSED_MIDS) > MAX_PROCESSED:
        # Bellek şişmesin diye kabaca temizle.
        PROCESSED_MIDS.clear()
    return True


def remember_bot_mid(mid: str):
    if mid:
        BOT_SENT_MIDS.add(mid)
        if len(BOT_SENT_MIDS) > MAX_PROCESSED:
            BOT_SENT_MIDS.clear()


def is_bot_echo(mid: str) -> bool:
    return bool(mid and mid in BOT_SENT_MIDS)


def can_reply(user_id: str) -> bool:
    user = get_user(user_id)
    if user["handoff"]:
        return False
    if user["bot_replies"] >= MAX_BOT_REPLIES_PER_USER:
        user["handoff"] = True
        return False
    if user_id in PROCESSING_USERS:
        return False
    return True


def lock_user(user_id: str) -> bool:
    if user_id in PROCESSING_USERS:
        return False
    PROCESSING_USERS.add(user_id)
    return True


def unlock_user(user_id: str):
    PROCESSING_USERS.discard(user_id)


def mark_handoff(user_id: str):
    user = get_user(user_id)
    user["handoff"] = True


def add_history(user_id: str, role: str, content: str):
    user = get_user(user_id)
    user["history"].append({"role": role, "content": content})
    user["history"] = user["history"][-10:]


def increment_reply(user_id: str):
    user = get_user(user_id)
    user["bot_replies"] += 1
    user["last_reply_time"] = time.time()
    if user["bot_replies"] >= MAX_BOT_REPLIES_PER_USER:
        user["handoff"] = True
