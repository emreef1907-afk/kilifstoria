from flask import Flask, request
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("emre123")
ACCESS_TOKEN = os.getenv("IGAATZBo0cEa55BZAFo0T0VsZADcwM0xBUnhnVGJZAWTVWX0dmUkhVMlh3b0dnZAjZAKOTl2dWpBbU1LWjVXeno4WkhQN1JDQV8tOG95aEdoNHlYWUFLR1pFNGI2VzlqRkNIUnRURWpXUmRxU1FseUhtVDgzVldnOEFCVHdubTE3MWloQQZDZD")

IG_API = "https://graph.instagram.com/v25.0/me/messages"


def send_message(recipient_id, text):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    r = requests.post(IG_API, headers=headers, json=payload)

    print("===== MESAJ GÖNDERME SONUCU =====", flush=True)
    print(r.status_code, flush=True)
    print(r.text, flush=True)


@app.route("/")
def home():
    return """
    <h1>Instagram Bot Çalışıyor!</h1>
    <p>KilifStoria otomatik mesaj botu aktif.</p>
    """


@app.route("/privacy")
def privacy():
    return """
    <h1>KilifStoria Gizlilik Politikası</h1>
    <p>KilifStoria, Instagram üzerinden gelen müşteri mesajlarını yanıtlamak ve sipariş sürecini yönetmek amacıyla Meta Instagram API kullanır.</p>
    <p>Toplanan veriler: Instagram kullanıcı ID, mesaj içeriği ve mesaj zamanı.</p>
    <p>Bu veriler üçüncü kişilerle satılmaz veya paylaşılmaz.</p>
    <p>Veri silme talepleri için: <b>emrelaydn02@gmail.com</b></p>
    """


@app.route("/terms")
def terms():
    return """
    <h1>KilifStoria Hizmet Şartları</h1>
    <p>Bu uygulama, Instagram mesajlarına otomatik yanıt vermek ve müşteri sipariş sürecini kolaylaştırmak amacıyla kullanılır.</p>
    <p>Kullanıcılar mesaj göndererek otomatik yanıt sisteminden hizmet almayı kabul eder.</p>
    <p>İletişim: <b>emrelaydn02@gmail.com</b></p>
    """


@app.route("/data-deletion")
def data_deletion():
    return """
    <h1>Veri Silme Talimatları</h1>
    <p>KilifStoria uygulamasında saklanan verilerinizin silinmesini istiyorsanız bize e-posta gönderin.</p>
    <p><b>E-posta:</b> emrelaydn02@gmail.com</p>
    <p>Talebiniz en geç 30 gün içinde işleme alınır.</p>
    """


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

    print("===== YENİ EVENT GELDİ =====", flush=True)
    print(json.dumps(data, indent=4, ensure_ascii=False), flush=True)

    for entry in data.get("entry", []):
        for item in entry.get("messaging", []):
            sender = item.get("sender", {})
            message = item.get("message", {})

            if sender.get("id") and message.get("text"):
                send_message(
                    sender["id"],
                    "Merhaba 😊 Telefon modelinizi yazar mısınız?"
                )

        for change in entry.get("changes", []):
            value = change.get("value", {})
            sender = value.get("sender", {})
            message = value.get("message", {})

            if sender.get("id") and message.get("text"):
                send_message(
                    sender["id"],
                    "Merhaba 😊 Telefon modelinizi yazar mısınız?"
                )

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)