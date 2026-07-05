from flask import Flask, request
from dotenv import load_dotenv
import os, requests, json

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "emre123")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_ID = "17841465752722469"

def send_message(user_id, text):
    url = f"https://graph.instagram.com/v25.0/{IG_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": text}
    }
    r = requests.post(url, headers=headers, json=payload)
    print("CEVAP SONUCU:", r.status_code, r.text)

@app.route("/")
def home():
    return "Instagram Bot Çalışıyor!"

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Doğrulama başarısız", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("\nYENİ EVENT GELDİ:")
    print(json.dumps(data, indent=4, ensure_ascii=False))

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            msg = value.get("message", {})
            sender = value.get("sender", {})

            if msg.get("text") and sender.get("id"):
                send_message(sender["id"], "Merhaba 😊 Telefon modelinizi yazar mısınız?")

        for item in entry.get("messaging", []):
            msg = item.get("message", {})
            sender = item.get("sender", {})

            if msg.get("text") and sender.get("id"):
                send_message(sender["id"], "Merhaba 😊 Telefon modelinizi yazar mısınız?")

    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)