import time
from config import MAX_BOT_REPLIES

users = {}
processed_mids = set()
processing_users = set()


def get_user(user_id: str) -> dict:
    if user_id not in users:
        users[user_id] = {
            "history": [],
            "handoff": False,
            "model": False,
            "design": False,
            "photo": False,
            "asked_more_questions": False,
            "bot_replies": 0,
            "last_reply_time": 0.0,
            "created_at": time.time(),
        }
    return users[user_id]


def add_history(user_id: str, role: str, content: str) -> None:
    user = get_user(user_id)
    user["history"].append({"role": role, "content": content})
    user["history"] = user["history"][-10:]


def mark_handoff(user_id: str) -> None:
    get_user(user_id)["handoff"] = True


def is_handoff(user_id: str) -> bool:
    return bool(get_user(user_id).get("handoff"))


def can_bot_reply(user_id: str) -> bool:
    user = get_user(user_id)
    if user.get("handoff"):
        return False
    return user.get("bot_replies", 0) < MAX_BOT_REPLIES


def register_bot_reply(user_id: str) -> None:
    user = get_user(user_id)
    user["bot_replies"] = user.get("bot_replies", 0) + 1
    user["last_reply_time"] = time.time()


def already_processed(mid: str | None) -> bool:
    if not mid:
        return False
    if mid in processed_mids:
        return True
    processed_mids.add(mid)
    if len(processed_mids) > 5000:
        # Basit temizlik: hafızanın şişmesini engeller.
        processed_mids.clear()
    return False
