from flask import Flask, request
from dotenv import load_dotenv
import os, requests, json

load_dotenv()
app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "emre123")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

IG_API = "https://graph.instagram.com/v25.0/me/messages"

# Kendi Instagram business id'lerin. Echo döngüsünü kesmek için.
OWN_IDS = {
    "17841465752722469",
    "27903058482613663"
}

def send_message(recipient_id, text):
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    r = requests.post(IG_API, headers=headers, json=payload)

    print("===== MESAJ GÖNDERME SONUCU =====", flush=True)
    print(r.status_code, flush=True)
    print(r.text, flush=True)


def cevap_uret(text):
    t = text.lower().strip()

    if any(x in t for x in ["fiyat", "kaç", "kac", "ücret", "ucret"]):
        return (
            "💸 Fiyatlarımız:\n\n"
            "Havale/EFT:\n"
            "• Tek kılıf 345₺\n"
            "• 2 adet ve üzeri tanesi 265₺\n\n"
            "Kapıda ödeme:\n"
            "• Tek kılıf 425₺\n"
            "• 2 adet ve üzeri tanesi 345₺\n\n"
            "🚚 81 ile ücretsiz kargo."
        )

    if any(x in t for x in ["iphone", "samsung", "xiaomi", "redmi", "oppo", "tecno", "realme", "huawei"]):
        return (
            "Harika 😊 Bu model için yardımcı olalım.\n\n"
            "Kılıf tasarımını seçtiniz mi, yoksa size modelleri göstereyim mi?"
        )

    if any(x in t for x in ["kapıda", "kapida", "ödeme", "odeme"]):
        return (
            "Evet kapıda ödeme mevcut 😊\n\n"
            "Kapıda ödeme:\n"
            "• Tek kılıf 425₺\n"
            "• 2 adet ve üzeri tanesi 345₺\n\n"
            "🚚 Kargo ücretsiz."
        )

    if any(x in t for x in ["merhaba", "selam", "sa", "slm", "hello", "hi"]):
        return "Merhaba 😊 KilifStoria'ya hoş geldiniz.\n\nTelefon modelinizi yazar mısınız?"

    return "Anladım 😊 Size yardımcı olabilmem için telefon modelinizi yazar mısınız?"


@app.route("/")
def home():
    return "<h1>Instagram Bot Çalışıyor!</h1><p>KilifStoria bot aktif.</p>"


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
    data = request.json

    print("===== YENİ EVENT GELDİ / BOT V2 =====", flush=True)
    print(json.dumps(data, indent=4, ensure_ascii=False), flush=True)

    for entry in data.get("entry", []):
        for item in entry.get("messaging", []):
            sender_id = item.get("sender", {}).get("id")
            message = item.get("message", {})
            text = message.get("text")

            if message.get("is_echo"):
                print("Echo atlandı.", flush=True)
                continue

            if sender_id in OWN_IDS:
                print("Kendi hesabımdan gelen event atlandı.", flush=True)
                continue

            if sender_id and text:
                cevap = cevap_uret(text)
                send_message(sender_id, cevap)

        for change in entry.get("changes", []):
            value = change.get("value", {})
            sender_id = value.get("sender", {}).get("id")
            message = value.get("message", {})
            text = message.get("text")

            if message.get("is_echo"):
                print("Echo atlandı.", flush=True)
                continue

            if sender_id in OWN_IDS:
                print("Kendi hesabımdan gelen event atlandı.", flush=True)
                continue

            if sender_id and text:
                cevap = cevap_uret(text)
                send_message(sender_id, cevap)

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)