from collections import OrderedDict
import time
import threading
from config import MAX_TRACKED_MIDS, MAX_HISTORY_MESSAGES

_lock = threading.RLock()

_users = {}
_processed_mids = OrderedDict()
_bot_sent_mids = OrderedDict()
_processing_mids = set()

# Aynı kullanıcının aynı mesajını kısa sürede iki kere işlememek için.
_last_inbound = {}

# Aynı kullanıcıya aynı cevabı kısa sürede iki kere atmamak için.
_last_outbound = {}

INBOUND_DEDUPE_SECONDS = 30
OUTBOUND_DEDUPE_SECONDS = 90


def _remember_limited(store: OrderedDict, key: str):
    if not key:
        return
    store[key] = time.time()
    while len(store) > MAX_TRACKED_MIDS:
        store.popitem(last=False)


def mark_processed(mid: str):
    with _lock:
        _remember_limited(_processed_mids, mid)


def is_processed(mid: str) -> bool:
    with _lock:
        return bool(mid and mid in _processed_mids)


def mark_bot_sent(mid: str):
    with _lock:
        _remember_limited(_bot_sent_mids, mid)


def is_bot_sent(mid: str) -> bool:
    with _lock:
        return bool(mid and mid in _bot_sent_mids)


def start_processing(mid: str) -> bool:
    with _lock:
        if not mid:
            return True
        if mid in _processing_mids:
            return False
        _processing_mids.add(mid)
        return True


def finish_processing(mid: str):
    with _lock:
        if mid:
            _processing_mids.discard(mid)


def get_user(user_id: str):
    with _lock:
        if user_id not in _users:
            _users[user_id] = {
                'history': [],
                'handoff': False,
                'model': False,
                'design': False,
                'photo': False,
                'asked_more_questions': False,
                'bot_replies': 0,
                'last_reply_time': 0,
            }
        return _users[user_id]


def append_history(user_id: str, role: str, content: str):
    with _lock:
        user = get_user(user_id)
        user['history'].append({'role': role, 'content': content})
        user['history'] = user['history'][-MAX_HISTORY_MESSAGES:]


def set_handoff(user_id: str, value: bool = True):
    with _lock:
        get_user(user_id)['handoff'] = value


def update_facts(user_id: str, *, model=None, design=None, photo=None, asked_more_questions=None):
    with _lock:
        user = get_user(user_id)
        if model is not None:
            user['model'] = bool(model) or user['model']
        if design is not None:
            user['design'] = bool(design) or user['design']
        if photo is not None:
            user['photo'] = bool(photo) or user['photo']
        if asked_more_questions is not None:
            user['asked_more_questions'] = bool(asked_more_questions) or user['asked_more_questions']


def _normalize_text(text: str) -> str:
    return ' '.join((text or '').lower().strip().split())


def inbound_signature(text: str, has_photo: bool = False) -> str:
    if has_photo and not text:
        return 'PHOTO_ONLY'
    return ('PHOTO:' if has_photo else 'TEXT:') + _normalize_text(text)


def is_duplicate_inbound(user_id: str, text: str, has_photo: bool = False, window: int = INBOUND_DEDUPE_SECONDS) -> bool:
    """Aynı müşteriden aynı içerik kısa sürede gelirse ikinciyi atlar."""
    if not user_id:
        return False
    sig = inbound_signature(text, has_photo)
    now = time.time()
    with _lock:
        last = _last_inbound.get(user_id)
        if last:
            last_sig, last_time = last
            if last_sig == sig and now - last_time < window:
                return True
        _last_inbound[user_id] = (sig, now)
        return False


def remember_outbound(user_id: str, text: str):
    if not user_id:
        return
    with _lock:
        _last_outbound[user_id] = (_normalize_text(text), time.time())


def is_duplicate_outbound(user_id: str, text: str, window: int = OUTBOUND_DEDUPE_SECONDS) -> bool:
    if not user_id:
        return False
    now = time.time()
    normalized = _normalize_text(text)
    with _lock:
        last = _last_outbound.get(user_id)
        if not last:
            return False
        last_text, last_time = last
        return last_text == normalized and now - last_time < window


def is_recent_bot_outbound(user_id: str, text: str, window: int = 180) -> bool:
    """Echo MID kaydı kaçarsa bile metinden botun kendi echo'sunu tanır."""
    return is_duplicate_outbound(user_id, text, window=window)
