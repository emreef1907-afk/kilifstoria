from flask import Flask, request
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

IG_API = "https://graph.instagram.com/v25.0/me/messages"


def send_message(recipient_id, text):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": text
        }
    }

    r = requests.post(IG_API, headers=headers, json=payload)

    print("\n===== MESAJ GÖNDERME SONUCU =====", flush=True)
    print(r.status_code, flush=True)
    print(r.text, flush=True)


@app.route("/")
def home():
    return "Instagram Bot Çalışıyor!"


@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("\n===============================", flush=True)
    print("YENİ EVENT GELDİ", flush=True)
    print("===============================", flush=True)
    print(json.dumps(data, indent=4, ensure_ascii=False), flush=True)

    # Instagram Messaging formatı
    for entry in data.get("entry", []):
        for item in entry.get("messaging", []):
            sender = item.get("sender", {})
            message = item.get("message", {})

            if sender.get("id") and message.get("text"):
                print("MESAJ ALGILANDI!", flush=True)
                print(sender["id"], flush=True)
                print(message["text"], flush=True)

                send_message(
                    sender["id"],
                    "Merhaba 😊 Telefon modelinizi yazar mısınız?"
                )

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    