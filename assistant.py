import json
import time
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, MAX_BOT_REPLIES
from knowledge import BUSINESS_FACTS, DIRECT_ANSWERS, HANDOFF_MESSAGE
from detectors import detect_phone_model, detect_design, detect_intent, detect_no_more_questions
from memory import get_user, append_history, update_facts, set_handoff

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

SYSTEM_PROMPT = f'''
Sen KilifStoria'nın Instagram DM karşılama asistanısın.

Amacın satış kapatmak değil; müşteriyi sıcak karşılamak, gerekli bilgileri almak, aklındaki soruları cevaplamak ve doğru zamanda ekip arkadaşına devretmektir.

Konuşma tarzı:
- Türkçe konuş.
- Kısa, sıcak, doğal ve samimi yaz.
- Robot gibi davranma.
- Gereksiz uzun paragraf yazma.
- Aynı cevabı tekrar etme.
- Uydurma bilgi verme.
- Tek mesajda mümkünse tek ana konuya odaklan.

Yapacakların:
- Telefon modelini öğren.
- İstenen tasarım türünü öğren: sayfadaki tasarımlardan biri, kendi fotoğrafı, isimli tasarım, özel tasarım.
- Müşteri görsel/fotoğraf gönderirse fotoğrafı aldığını kabul et; tekrar fotoğraf isteme.
- Müşterinin fiyat/kargo/ödeme/teslimat/baskı kalitesi gibi sorularını doğru cevapla.
- Telefon modeli ve tasarım isteği alındıktan sonra hemen devretme; önce “Aklınıza takılan başka bir soru var mı?” gibi kısa sor.
- Müşteri başka soru yok derse sadece devretme mesajını yaz.

Asla yapma:
- Sipariş alma.
- Adres isteme.
- Telefon numarası isteme.
- Ad soyad isteme.
- IBAN gönderme.
- Tasarım hazırlama veya onaylama.
- Kargo takip verme.

Devretme mesajı tam olarak şudur; ek cümle ekleme:
{HANDOFF_MESSAGE}

Bilgi tabanı:
{BUSINESS_FACTS}

Yanıtını SADECE JSON olarak ver:
{{
  "reply": "müşteriye gönderilecek kısa mesaj",
  "handoff": true veya false,
  "facts": {{
    "model": true veya false,
    "design": true veya false,
    "photo": true veya false,
    "asked_more_questions": true veya false
  }}
}}
'''


def _state_text(user_id: str):
    user = get_user(user_id)
    return json.dumps({
        'telefon_modeli_alindi': user['model'],
        'tasarim_istegi_alindi': user['design'],
        'foto_geldi': user['photo'],
        'aklinda_baska_soru_soruldu': user['asked_more_questions'],
        'bot_cevap_sayisi': user['bot_replies'],
    }, ensure_ascii=False)


def _direct_reply(user_id: str, text: str):
    intent = detect_intent(text)
    if not intent:
        return None

    reply = DIRECT_ANSWERS[intent]
    user = get_user(user_id)

    # Direkt cevaplardan sonra konuşmayı amaca döndür.
    if not user['model'] and intent not in ['model_missing']:
        reply += '\n\nBu arada hangi telefon modeli için düşünüyorsunuz? 😊'
    elif user['model'] and not user['design'] and intent not in ['designs']:
        reply += '\n\nNasıl bir tasarım düşünüyorsunuz; sayfadaki tasarımlardan biri mi, kendi fotoğrafınız mı, isimli ya da özel tasarım mı?'
    elif user['model'] and user['design'] and not user['asked_more_questions']:
        user['asked_more_questions'] = True
        reply += '\n\nAklınıza takılan başka bir soru var mı? 😊'

    return reply


def create_reply(user_id: str, text: str, has_photo: bool = False):
    user = get_user(user_id)

    if user['handoff']:
        print('Kullanıcı devredilmiş, cevap yok:', user_id, flush=True)
        return None

    if user['bot_replies'] >= MAX_BOT_REPLIES:
        set_handoff(user_id, True)
        return HANDOFF_MESSAGE

    # Durum güncelle
    update_facts(
        user_id,
        model=detect_phone_model(text),
        design=detect_design(text, has_photo),
        photo=has_photo,
    )
    user = get_user(user_id)

    if user['model'] and user['design'] and user['asked_more_questions'] and detect_no_more_questions(text):
        set_handoff(user_id, True)
        return HANDOFF_MESSAGE

    direct = _direct_reply(user_id, text)
    if direct:
        reply = direct
        handoff = False
    else:
        if has_photo:
            text = text + '\nMüşteri görsel/fotoğraf gönderdi.'

        append_history(user_id, 'user', text)
        user = get_user(user_id)

        conversation = f'Müşteri durumu: {_state_text(user_id)}\n\n'
        for msg in user['history'][-8:]:
            role = 'Müşteri' if msg['role'] == 'user' else 'KilifStoria'
            conversation += f'{role}: {msg["content"]}\n'

        if not client:
            raise RuntimeError('OPENAI_API_KEY eksik. Render Environment içine OPENAI_API_KEY eklenmeli.')

        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=conversation,
            max_output_tokens=180,
        )

        raw = response.output_text.strip()
        print('GPT RAW:', raw, flush=True)

        try:
            parsed = json.loads(raw)
            reply = (parsed.get('reply') or '').strip()
            handoff = bool(parsed.get('handoff', False))
            facts = parsed.get('facts') or {}
            update_facts(
                user_id,
                model=facts.get('model'),
                design=facts.get('design'),
                photo=facts.get('photo'),
                asked_more_questions=facts.get('asked_more_questions'),
            )
        except Exception:
            reply = raw
            handoff = False

    user = get_user(user_id)

    if not reply:
        reply = 'Merhaba 😊 Hangi telefon modeli için kılıf düşünüyorsunuz?'

    # Model + tasarım tamamlandıysa, önce son soru fırsatı ver.
    if user['model'] and user['design'] and not user['asked_more_questions'] and not handoff:
        user['asked_more_questions'] = True
        if 'aklınıza takılan' not in reply.lower():
            reply += '\n\nAklınıza takılan başka bir soru var mı? 😊'

    if handoff:
        set_handoff(user_id, True)
        reply = HANDOFF_MESSAGE

    user['bot_replies'] += 1
    user['last_reply_time'] = time.time()
    append_history(user_id, 'assistant', reply)

    return reply
