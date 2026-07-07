import time
from typing import Dict, Any

_users: Dict[str, Dict[str, Any]] = {}
_processed_mids = set()
_bot_sent_mids = set()
_locks = set()


def get_user(user_id: str) -> Dict[str, Any]:
    if user_id not in _users:
        _users[user_id] = {
            "history": [],
            "handoff": False,
            "manual": False,
            "model": None,
            "design": None,
            "photo": False,
            "asked_more_questions": False,
            "last_incoming_text": "",
            "last_incoming_time": 0.0,
            "last_reply": "",
            "last_reply_time": 0.0,
        }
    return _users[user_id]


def mark_processed_mid(mid: str) -> bool:
    """True dönerse bu mid daha önce işlenmemiştir; False ise tekrar gelmiştir."""
    if not mid:
        return True
    if mid in _processed_mids:
        return False
    _processed_mids.add(mid)
    return True


def remember_bot_mid(mid: str):
    if mid:
        _bot_sent_mids.add(mid)


def is_bot_mid(mid: str) -> bool:
    return bool(mid and mid in _bot_sent_mids)


def acquire_lock(user_id: str) -> bool:
    if user_id in _locks:
        return False
    _locks.add(user_id)
    return True


def release_lock(user_id: str):
    _locks.discard(user_id)


def mark_manual_handoff(user_id: str):
    user = get_user(user_id)
    user["handoff"] = True
    user["manual"] = True


def update_history(user_id: str, role: str, content: str, limit: int = 10):
    user = get_user(user_id)
    user["history"].append({"role": role, "content": content})
    user["history"] = user["history"][-limit:]


def duplicate_incoming(user_id: str, text: str, window: int) -> bool:
    user = get_user(user_id)
    now = time.time()
    clean = (text or "").strip().lower()
    if clean and clean == user.get("last_incoming_text") and now - user.get("last_incoming_time", 0) < window:
        return True
    user["last_incoming_text"] = clean
    user["last_incoming_time"] = now
    return False


def duplicate_reply(user_id: str, reply: str, window: int) -> bool:
    user = get_user(user_id)
    now = time.time()
    clean = (reply or "").strip().lower()
    if clean and clean == user.get("last_reply") and now - user.get("last_reply_time", 0) < window:
        return True
    return False


def mark_reply_sent(user_id: str, reply: str):
    user = get_user(user_id)
    user["last_reply"] = (reply or "").strip().lower()
    user["last_reply_time"] = time.time()
