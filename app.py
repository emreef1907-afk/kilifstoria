from flask import Flask, request
from dotenv import load_dotenv
import os, json, requests

load_dotenv()
app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "emre123")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_API = "https://graph.instagram.com/v25.0/me/messages"

OWN_IDS = {"17841465752722469", "27903058482613663"}

users = {}

def send_message(user_id, text):
    r = requests.post(
        IG_API,
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "recipient": {"id": user_id},
            "message": {"text": text[:950]}
        }
    )
    print("MESAJ SONUCU:", r.status_code, r.text, flush=True)

def get_state(user_id):
    if user_id not in users:
        users[user_id] = {
            "model": False,
            "istek": False,
            "handoff": False
        }
    return users[user_id]

def cevap_uret(user_id, text):
    state = get_state(user_id)
    t = text.lower().strip()

    if state["handoff"]:
        return None

    if any(x in t for x in ["fiyat", "kaç", "kac", "ücret", "ucret", "tl"]):
        return (
            "Fiyatlarımız şöyle 😊\n\n"
            "💸 Havale/EFT:\n"
            "• Tek kılıf 345₺\n"
            "• 2 adet ve üzeri tanesi 265₺\n\n"
            "📦 Kapıda ödeme:\n"
            "• Tek kılıf 425₺\n"
            "• 2 adet ve üzeri tanesi 345₺\n\n"
            "🚚 Kargo ücretsiz."
        )

    if any(x in t for x in ["kargo", "hangi firma", "firma", "ptt"]):
        return "Gönderimlerimizi PTT Kargo ile sağlıyoruz 😊 81 ile ücretsiz kargo mevcut."

    if any(x in t for x in ["kaç günde", "ne zaman gelir", "teslimat", "kaç gün"]):
        return "Sipariş hazırlandıktan sonra teslimat genelde 2-4 iş günü içinde oluyor 😊"

    if any(x in t for x in ["iphone", "samsung", "xiaomi", "redmi", "oppo", "tecno", "realme", "huawei", "honor", "vivo"]):
        state["model"] = True
        if not state["istek"]:
            return (
                "Harika 😊 Bu model için yardımcı olabiliriz.\n\n"
                "Nasıl bir tasarım istiyorsunuz?\n"
                "1️⃣ Sayfamızdaki tasarımlardan mı?\n"
                "2️⃣ Kendi fotoğrafınızla mı?\n"
                "3️⃣ İsimli / taclı özel tasarım mı?"
            )

    if any(x in t for x in ["sayfadaki", "sayfanızdaki", "tasarım", "fotoğraf", "fotograf", "isim", "isimli", "taç", "tac", "özel", "ozel"]):
        state["istek"] = True

    if not state["model"]:
        return "Merhaba 😊 KilifStoria’ya hoş geldiniz. Hangi telefon modeli için kılıf düşünüyorsunuz?"

    if state["model"] and not state["istek"]:
        return (
            "Tamamdır 😊 Nasıl bir tasarım istiyorsunuz?\n\n"
            "1️⃣ Sayfamızdaki tasarımlardan mı?\n"
            "2️⃣ Kendi fotoğrafınızla mı?\n"
            "3️⃣ İsimli / taclı özel tasarım mı?"
        )

    if state["model"] and state["istek"]:
        state["handoff"] = True
        return "Harika 😊 Bilgileri aldım. Tasarım ve sipariş işlemi için ekip arkadaşımız birazdan size dönüş yapacak."

    return "Anladım 😊 Size daha iyi yardımcı olabilmem için telefon modelinizi yazar mısınız?"

@app.route("/")
def home():
    return "<h1>Instagram Bot Çalışıyor!</h1><p>KilifStoria karşılama botu aktif.</p>"

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
    print("===== EVENT GELDİ =====", flush=True)
    print(json.dumps(data, indent=4, ensure_ascii=False), flush=True)

    for entry in data.get("entry", []):
        for item in entry.get("messaging", []):
            sender_id = item.get("sender", {}).get("id")
            message = item.get("message", {})
            text = message.get("text")

            if message.get("is_echo"):
                continue

            if sender_id in OWN_IDS:
                continue

            if sender_id and text:
                cevap = cevap_uret(sender_id, text)
                if cevap:
                    send_message(sender_id, cevap)

    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)