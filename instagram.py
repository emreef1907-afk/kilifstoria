import requests
from config import ACCESS_TOKEN, IG_API
from memory import remember_bot_mid


def send_message(user_id: str, text: str) -> bool:
    if not ACCESS_TOKEN:
        print("ACCESS_TOKEN yok, mesaj gönderilemedi.", flush=True)
        return False

    payload = {
        "recipient": {"id": user_id},
        "message": {"text": text[:900]},
    }

    response = requests.post(
        IG_API,
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
        # Instagram genelde message_id döndürür.
        remember_bot_mid(data.get("message_id") or data.get("mid"))
    except Exception:
        pass

    return response.ok
