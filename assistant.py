import json, time
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, HANDOFF_MESSAGE, MIN_SECONDS_BETWEEN_REPLIES
from knowledge import SYSTEM_PROMPT
from memory import get_user, remember_reply, mark_handoff
from detectors import detect_model, detect_design, quick_answer, is_no_more_questions

client = OpenAI(api_key=OPENAI_API_KEY)


def update_state(user, text, has_photo):
    if has_photo:
        user['photo'] = True
        user['design'] = True
    if detect_model(text):
        user['model'] = True
    if detect_design(text):
        user['design'] = True


def build_conversation(user, text, has_photo):
    user['history'].append({'role': 'user', 'content': text})
    user['history'] = user['history'][-8:]
    state_info = {
        'telefon_modeli_alindi': user['model'],
        'tasarim_istegi_alindi': user['design'],
        'foto_geldi': user['photo'],
        'aklinda_baska_soru_soruldu': user['asked_more_questions'],
        'bot_cevap_sayisi': user['bot_replies']
    }
    convo = f'Müşteri durumu: {json.dumps(state_info, ensure_ascii=False)}\n\n'
    for msg in user['history']:
        role = 'Müşteri' if msg['role'] == 'user' else 'KilifStoria'
        convo += f'{role}: {msg["content"]}\n'
    if has_photo:
        convo += '\nMüşteri fotoğraf/görsel gönderdi. Bunu dikkate al.\n'
    return convo


def create_reply(user_id, text, has_photo=False):
    user = get_user(user_id)
    if user['handoff']:
        return None
    now = time.time()
    if now - user['last_reply_time'] < MIN_SECONDS_BETWEEN_REPLIES:
        print('Çok hızlı tekrar, atlandı.', flush=True)
        return None

    update_state(user, text, has_photo)

    if user['model'] and user['design'] and user['asked_more_questions'] and is_no_more_questions(text):
        mark_handoff(user_id)
        return HANDOFF_MESSAGE

    direct = quick_answer(text)
    if direct:
        reply = direct
        handoff = False
    else:
        convo = build_conversation(user, text, has_photo)
        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=convo,
            max_output_tokens=180
        )
        raw = response.output_text.strip()
        print('GPT RAW:', raw, flush=True)
        try:
            parsed = json.loads(raw)
            if not parsed.get('should_reply', True):
                return None
            reply = parsed.get('reply', '').strip()
            handoff = bool(parsed.get('handoff', False))
            facts = parsed.get('facts', {}) or {}
            if facts.get('model'):
                user['model'] = True
            if facts.get('design'):
                user['design'] = True
            if facts.get('photo'):
                user['photo'] = True
            if facts.get('asked_more_questions'):
                user['asked_more_questions'] = True
        except Exception:
            reply = raw
            handoff = False

    if user['model'] and user['design'] and not user['asked_more_questions']:
        user['asked_more_questions'] = True
        reply = (reply or '').strip() + '\n\nAklınıza takılan başka bir soru var mı? 😊'
        handoff = False

    if handoff:
        mark_handoff(user_id)
        reply = HANDOFF_MESSAGE

    if not reply:
        return None
    if not remember_reply(user_id, reply):
        print('Aynı cevap yakın zamanda gönderilmiş, atlandı.', flush=True)
        return None

    user['bot_replies'] += 1
    user['last_reply_time'] = time.time()
    user['history'].append({'role': 'assistant', 'content': reply})
    user['history'] = user['history'][-8:]
    if user['bot_replies'] >= 5:
        user['handoff'] = True
    return reply
