from collections import OrderedDict
from config import MAX_TRACKED_MIDS, MAX_HISTORY_MESSAGES

_users = {}
_processed_mids = OrderedDict()
_bot_sent_mids = OrderedDict()
_processing_mids = set()


def _remember_limited(store: OrderedDict, key: str):
    if not key:
        return
    store[key] = True
    while len(store) > MAX_TRACKED_MIDS:
        store.popitem(last=False)


def mark_processed(mid: str):
    _remember_limited(_processed_mids, mid)


def is_processed(mid: str) -> bool:
    return bool(mid and mid in _processed_mids)


def mark_bot_sent(mid: str):
    _remember_limited(_bot_sent_mids, mid)


def is_bot_sent(mid: str) -> bool:
    return bool(mid and mid in _bot_sent_mids)


def start_processing(mid: str) -> bool:
    if not mid:
        return True
    if mid in _processing_mids:
        return False
    _processing_mids.add(mid)
    return True


def finish_processing(mid: str):
    if mid:
        _processing_mids.discard(mid)


def get_user(user_id: str):
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
    user = get_user(user_id)
    user['history'].append({'role': role, 'content': content})
    user['history'] = user['history'][-MAX_HISTORY_MESSAGES:]


def set_handoff(user_id: str, value: bool = True):
    get_user(user_id)['handoff'] = value


def update_facts(user_id: str, *, model=None, design=None, photo=None, asked_more_questions=None):
    user = get_user(user_id)
    if model is not None:
        user['model'] = bool(model) or user['model']
    if design is not None:
        user['design'] = bool(design) or user['design']
    if photo is not None:
        user['photo'] = bool(photo) or user['photo']
    if asked_more_questions is not None:
        user['asked_more_questions'] = bool(asked_more_questions) or user['asked_more_questions']
