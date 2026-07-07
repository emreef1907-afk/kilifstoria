from flask import Flask, request
import json

from config import VERIFY_TOKEN, PORT, DUPLICATE_TEXT_WINDOW_SECONDS
from memory import (
    mark_processed_mid, is_bot_mid, mark_manual_handoff, acquire_lock, release_lock,
    duplicate_incoming
)
from assistant import create_reply
from instagram import send_message

app = Flask(__name__)


@app.route("/")
def home():
    return "<h1>Instagram Bot Çalışıyor!</h1><p>KilifStoria AI V4 aktif.</p>"


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
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}
    print("===== EVENT GELDİ / KILIFSTORIA AI V4 =====", flush=True)
    print(json.dumps(data, indent=4, ensure_ascii=False), flush=True)

    for entry in data.get("entry", []):
        for item in entry.get("messaging", []):
            sender_id = item.get("sender", {}).get("id")
            recipient_id = item.get("recipient", {}).get("id")
            message = item.get("message", {}) or {}
            mid = message.get("mid")

            # Aynı webhook olayı tekrar gelirse işleme alma.
            if mid and not mark_processed_mid(mid):
                print("Aynı MID tekrar geldi, atlandı.", flush=True)
                continue

            # Echo ayrımı: botun kendi echo'su susturmaz; manuel cevap susturur.
            if message.get("is_echo"):
                if is_bot_mid(mid):
                    print("Botun kendi echo mesajı atlandı.", flush=True)
                    continue
                if recipient_id:
                    mark_manual_handoff(recipient_id)
                    print(f"Manuel cevap algılandı. {recipient_id} için bot susturuldu.", flush=True)
                continue

            text = message.get("text", "") or ""
            attachments = message.get("attachments", []) or []
            has_photo = bool(attachments)

            if not sender_id or not (text or has_photo):
                continue

            if not acquire_lock(sender_id):
                print("Kullanıcı zaten işleniyor, ikinci işlem atlandı.", flush=True)
                continue

            try:
                if not text and has_photo:
                    text = "Müşteri fotoğraf gönderdi."

                if duplicate_incoming(sender_id, text, DUPLICATE_TEXT_WINDOW_SECONDS):
                    print("Aynı içerik kısa sürede tekrar geldi, atlandı.", flush=True)
                    continue

                reply = create_reply(sender_id, text, has_photo)
                if reply:
                    send_message(sender_id, reply)
            except Exception as exc:
                print("BOT HATASI:", str(exc), flush=True)
            finally:
                release_lock(sender_id)

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
