import time
import requests
from config import ACCESS_TOKEN, IG_API_URL


def send_message(user_id: str, text: str) -> None:
    # Robot gibi anlık basmasın diye kısa gecikme.
    time.sleep(2)
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": text[:900]},
    }
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    response = requests.post(IG_API_URL, headers=headers, json=payload, timeout=20)
    print("MESAJ SONUCU:", response.status_code, response.text, flush=True)
