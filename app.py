from flask import Flask, request
from dotenv import load_dotenv
import os, json

load_dotenv()

from config import VERIFY_TOKEN, OWN_IDS
from memory import get_user, mark_handoff, already_processed, processing_users
from assistant import generate_reply
from instagram import send_message

app = Flask(__name__)


@app.route("/")
def home():
    return "<h1>Instagram Bot Çalışıyor!</h1><p>KilifStoria AI V3 aktif.</p>"


@app.route("/privacy")
def privacy():
    return "<h1>KilifStoria Gizlilik Politikası</h1><p>Veri silme talepleri: emrelaydn02@gmail.com</p>"


@app.route("/terms")
def terms():
    return "<h1>KilifStoria Hizmet Şartları</h1><p>KilifStoria otomatik mesaj botu.</p>"


@app.route("/data-deletion")
def data_deletion():
    return "<h1>Veri Silme Talimatları</h1><p>Veri silme talepleri: emrelaydn02@gmail.com</p>"


@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}
    print("===== EVENT GELDİ / KILIFSTORIA AI V3 =====", flush=True)
    print(json.dumps(data, indent=4, ensure_ascii=False), flush=True)

    for entry in data.get("entry", []):
        for item in entry.get("messaging", []):
            sender_id = item.get("sender", {}).get("id")
            recipient_id = item.get("recipient", {}).get("id")
            message = item.get("message", {})

            # Sen manuel cevap yazınca echo event gelir. Bu müşteride botu kapat.
            if message.get("is_echo"):
                if message.get("is_echo"):
    print("Bot/hesap echo mesajı geldi, atlandı. Müşteri susturulmadı.", flush=True)
    continue

            if not sender_id or sender_id in OWN_IDS:
                continue

            mid = message.get("mid")
            if already_processed(mid):
                print("Aynı mid tekrar geldi, atlandı.", flush=True)
                continue

            if sender_id in processing_users:
                print("Kullanıcı zaten işleniyor, ikinci event atlandı.", flush=True)
                continue

            text = message.get("text", "")
            attachments = message.get("attachments", []) or []
            has_photo = bool(attachments)

            if not text and has_photo:
                text = "Müşteri fotoğraf gönderdi."

            if not text and not has_photo:
                continue

            try:
                processing_users.add(sender_id)
                reply = generate_reply(sender_id, text, has_photo=has_photo)
                if reply:
                    send_message(sender_id, reply)
            except Exception as exc:
                print("BOT HATASI:", str(exc), flush=True)
                send_message(sender_id, "Merhaba 😊 Hangi telefon modeli için kılıf düşünüyorsunuz?")
            finally:
                processing_users.discard(sender_id)

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
