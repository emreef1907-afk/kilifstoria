import requests, time
from config import ACCESS_TOKEN, IG_API
from memory import bot_sent_mids


def send_message(user_id, text):
    time.sleep(2)
    r = requests.post(
        IG_API,
        headers={
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        },
        json={'recipient': {'id': user_id}, 'message': {'text': text[:900]}}
    )
    print('MESAJ SONUCU:', r.status_code, r.text, flush=True)
    try:
        data = r.json()
        mid = data.get('message_id')
        if mid:
            bot_sent_mids.add(mid)
            print('Bot mesaj MID kaydedildi:', mid, flush=True)
    except Exception as e:
        print('MID kaydedilemedi:', str(e), flush=True)
    return r
