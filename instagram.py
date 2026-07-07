import random
import time
import requests
from config import ACCESS_TOKEN, IG_API_URL, MAX_REPLY_CHARS, MIN_SECONDS_BETWEEN_REPLIES, MAX_SECONDS_DELAY
from memory import remember_bot_mid, mark_reply_sent


def send_message(user_id: str, text: str):
    delay = random.randint(MIN_SECONDS_BETWEEN_REPLIES, MAX_SECONDS_DELAY)
    print(f"Cevap gecikmesi: {delay} sn", flush=True)
    time.sleep(delay)

    payload = {
        "recipient": {"id": user_id},
        "message": {"text": text[:MAX_REPLY_CHARS]},
    }

    response = requests.post(
        IG_API_URL,
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=20,
    )

    print("MESAJ SONUCU:", response.status_code, response.text, flush=True)

    try:
        data = response.json()
        mid = data.get("message_id")
        if mid:
            remember_bot_mid(mid)
            print("Bot mesaj MID kaydedildi:", mid, flush=True)
    except Exception as exc:
        print("Bot MID kaydedilemedi:", str(exc), flush=True)

    mark_reply_sent(user_id, text)
    return response
