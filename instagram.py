import requests
import time
from config import ACCESS_TOKEN, IG_API_URL
from memory import mark_bot_sent, remember_outbound, is_duplicate_outbound


def send_message(user_id: str, text: str):
    if is_duplicate_outbound(user_id, text):
        print('Aynı cevap kısa sürede zaten gönderildi, tekrar atlanıyor.', flush=True)
        return None

    if not ACCESS_TOKEN:
        raise RuntimeError('ACCESS_TOKEN eksik. Render Environment içinde ACCESS_TOKEN olmalı.')

    # İnsan gibi biraz beklesin, spam gibi seri atmasın.
    time.sleep(2)

    response = requests.post(
        IG_API_URL,
        headers={
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json',
        },
        json={
            'recipient': {'id': user_id},
            'message': {'text': text[:900]},
        },
        timeout=20,
    )

    print('MESAJ SONUCU:', response.status_code, response.text, flush=True)

    try:
        data = response.json()
        mid = data.get('message_id')
        if mid:
            mark_bot_sent(mid)
            print('Bot mesaj MID kaydedildi:', mid, flush=True)
    except Exception as exc:
        print('Bot MID kaydedilemedi:', str(exc), flush=True)

    if 200 <= response.status_code < 300:
        remember_outbound(user_id, text)

    return response
