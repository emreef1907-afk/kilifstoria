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

PHONE_WORDS = [
    "iphone", "samsung", "xiaomi", "redmi", "oppo", "tecno",
    "realme", "huawei", "honor", "vivo", "infinix", "poco",
    "galaxy", "note", "pro", "max", "plus", "a", "s"
]

DESIGN_WORDS = [
    "sayfadaki", "sayfanızdaki", "sayfanizdaki", "tasarım", "tasarim",
    "fotoğraf", "fotograf", "foto", "resim", "isim", "isimli",
    "taç", "tac", "özel", "ozel", "kendi fotoğrafım", "kendi fotografim"
]

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

def state(user_id):
    if user_id not in users:
        users[user_id] = {
            "step": "new",
            "model": None,
            "design": None,
            "handoff": False
        }
    return users[user_id]

def is_price(t):
    return any(x in t for x in ["fiyat", "kaç", "kac", "ücret", "ucret", "tl", "para"])

def is_cargo(t):
    return any(x in t for x in ["kargo", "hangi firma", "firma", "ptt"])

def is_delivery(t):
    return any(x in t for x in ["kaç günde", "kac gunde", "ne zaman gelir", "teslimat", "kaç gün", "kac gun"])

def is_phone_model(t):
    return any(x in t for x in PHONE_WORDS) and len(t) >= 3

def is_design(t):
    return any(x in t for x in DESIGN_WORDS)

def cevap_uret(user_id, text):
    s = state(user_id)
    t = text.lower().strip()

    if s["handoff"]:
        return None

    if is_price(t):
        return (
            "Fiyatlarımız şöyle 😊\n\n"
            "💸 Havale/EFT:\n"
            "• Tek kılıf 345₺\n"
            "• 2 adet ve üzeri tanesi 265₺\n\n"
            "📦 Kapıda ödeme:\n"
            "• Tek kılıf 425₺\n"
            "• 2 adet ve üzeri tanesi 345₺\n\n"
            "🚚 Kargo ücretsiz.\n\n"
            "Telefon modelinizi yazarsanız uygunluk konusunda da yardımcı olayım."
        )

    if is_cargo(t):
        return "Gönderimleri PTT Kargo ile sağlıyoruz 😊 Kargo 81 ile ücretsiz."

    if is_delivery(t):
        return "Sipariş hazırlandıktan sonra teslimat genelde 2-4 iş günü içinde oluyor 😊"

    if is_phone_model(t) and not s["model"]:
        s["model"] = text.strip()
        s["step"] = "model_alindi"
        return (
            f"Harika 😊 {text.strip()} için yardımcı olabiliriz.\n\n"
            "Nasıl bir tasarım istiyorsunuz?\n"
            "1️⃣ Sayfamızdaki tasarımlardan mı?\n"
            "2️⃣ Kendi fotoğrafınızla mı?\n"
            "3️⃣ İsimli / taclı özel tasarım mı?"
        )

    if is_phone_model(t) and s["model"] and not s["design"]:
        return (
            f"{s['model']} modelini aldım 😊\n\n"
            "Şimdi nasıl bir tasarım istediğinizi öğrenelim:\n"
            "1️⃣ Sayfamızdaki tasarımlardan mı?\n"
            "2️⃣ Kendi fotoğrafınızla mı?\n"
            "3️⃣ İsimli / taclı özel tasarım mı?"
        )

    if is_design(t) or t in ["1", "2", "3"]:
        if t == "1":
            s["design"] = "Sayfadaki tasarımlar"
        elif t == "2":
            s["design"] = "Kendi fotoğrafı"
        elif t == "3":
            s["design"] = "İsimli / taclı özel tasarım"
        else:
            s["design"] = text.strip()

        if not s["model"]:
            s["step"] = "tasarim_alindi_model_bekliyor"
            return "Çok güzel 😊 Hangi telefon modeli için olacak?"

        s["handoff"] = True
        return "Harika 😊 Bilgileri aldım. Tasarım ve sipariş işlemi için ekip arkadaşımız birazdan size dönüş yapacak."

    if s["step"] == "new":
        s["step"] = "model_bekliyor"
        return "Merhaba 😊 KilifStoria’ya hoş geldiniz. Hangi telefon modeli için kılıf düşünüyorsunuz?"

    if s["model"] and not s["design"]:
        return (
            "Tamamdır 😊 Nasıl bir tasarım istiyorsunuz?\n\n"
            "1️⃣ Sayfamızdaki tasarımlardan mı?\n"
            "2️⃣ Kendi fotoğrafınızla mı?\n"
            "3️⃣ İsimli / taclı özel tasarım mı?"
        )

    return "Anladım 😊 Telefon modelinizi ve nasıl bir tasarım istediğinizi yazarsanız yardımcı olayım."

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

    print("===== EVENT GELDİ / HANDOFF BOT =====", flush=True)
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