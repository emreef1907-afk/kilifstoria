from flask import Flask, request
from dotenv import load_dotenv
from openai import OpenAI
import os, json, requests, re

load_dotenv()
app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "emre123")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

IG_API = "https://graph.instagram.com/v25.0/me/messages"

OWN_IDS = {"17841465752722469", "27903058482613663"}

users = {}

SYSTEM_PROMPT = """
Sen KilifStoria'nın Instagram DM karşılama asistanısın.

Görevin:
- Müşteriyi sıcak ve doğal karşıla.
- Telefon modelini öğren.
- Nasıl bir kılıf istediğini öğren.
- Temel soruları cevapla.
- Tasarım oluşturma, sipariş alma, adres/telefon/ad-soyad isteme.
- Yeterli bilgi alınca konuşmayı ekip arkadaşına devret ve sus.

İşletme bilgileri:
- Tüm telefon marka ve modellerine üretim yapılır.
- Sayfadaki modeller sadece örnek tasarımdır.
- Müşteri beğendiği tasarımı seçer, biz kendi cihazına uygun hazırlarız.
- PTT Kargo ile gönderim yapılır.
- Teslimat ortalama 4 iş günü.
- Sipariş ertesi gün hazırlanır.
- Ödeme seçenekleri: Havale/EFT, kapıda ödeme, Shopier.
- Shopier: www.shopier.com/kilifstorie

Fiyatlar:
Havale/EFT:
• Tek Kılıf 345₺
• 2 Adet ve Üzeri 265₺ / Adet

Kapıda Ödeme:
• Tek Kılıf 425₺
• 2 Adet ve Üzeri 345₺ / Adet

Kargo:
🚚 81 ile ücretsiz kargo.
🔥 Havale ödemede en avantajlı fiyat.
🎁 2 ve üzeri siparişlerde büyük fiyat avantajı.

Konuşma tarzı:
- Türkçe konuş.
- Samimi, sıcak, kısa ve doğal ol.
- Robot gibi davranma.
- Gereksiz uzun yazma.
- Uydurma bilgi verme.
- Aynı soruyu tekrar tekrar sorma.
- Müşteri fotoğraf gönderdiyse “fotoğrafı aldım” mantığıyla devam et.
- Müşteri tasarım görmek isterse Instagram profiline veya Shopier’e yönlendir.
- Müşteri “telefonuma uygun model yok” derse, modellerin örnek tasarım olduğunu ve tüm cihazlara üretim yapıldığını söyle.

Devretme mesajı:
“Harika 😊 Bilgileri aldım. Tasarım ve sipariş işlemi için ekip arkadaşımız birazdan size dönüş yapacak.”

Cevabı SADECE JSON ver:
{
  "reply": "müşteriye gönderilecek mesaj",
  "handoff": true veya false
}
"""

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

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "history": [],
            "handoff": False,
            "model": False,
            "design": False,
            "photo": False,
            "bot_replies": 0
        }
    return users[user_id]

def detect_model(text):
    t = text.lower()
    brands = [
        "iphone", "samsung", "xiaomi", "redmi", "oppo", "tecno",
        "realme", "huawei", "honor", "vivo", "infinix", "poco",
        "galaxy", "a55", "a54", "a34", "s23", "s24", "13", "14", "15", "16"
    ]
    return any(x in t for x in brands) and len(t.strip()) >= 2

def detect_design(text):
    t = text.lower()
    words = [
        "isim", "isimli", "taç", "tac", "taclı", "foto", "fotoğraf",
        "fotograf", "resim", "kendi", "özel", "ozel", "sayfadaki",
        "tasarım", "tasarim", "model", "1", "2", "3"
    ]
    return any(x in t for x in words)

def known_answer(text):
    t = text.lower()

    if any(x in t for x in ["telefonuma uygun", "model yok", "cihazım yok", "cihazim yok", "uygun model"]):
        return "Hiç sorun değil 😊 Sayfamızdaki telefon modelleri sadece örnek tasarımdır. Beğendiğiniz tasarımı seçmeniz yeterli, biz tüm telefon marka ve modellerine uygun şekilde hazırlıyoruz. Telefon modeliniz nedir?"

    if any(x in t for x in ["fiyat", "kaç", "kac", "ücret", "ucret", "tl", "para"]):
        return (
            "Fiyatlarımız şöyle 😊\n\n"
            "💸 Havale / EFT\n"
            "• Tek Kılıf 345₺\n"
            "• 2 Adet ve Üzeri 265₺ / Adet\n\n"
            "💸 Kapıda Ödeme\n"
            "• Tek Kılıf 425₺\n"
            "• 2 Adet ve Üzeri 345₺ / Adet\n\n"
            "🚚 81 ile ücretsiz kargo.\n"
            "🔥 Havale ödemede en avantajlı fiyat.\n"
            "🎁 2 ve üzeri siparişlerde büyük fiyat avantajı."
        )

    if any(x in t for x in ["kargo", "hangi firma", "firma", "ptt"]):
        return "Gönderimlerimizi PTT Kargo ile sağlıyoruz 😊 81 ile ücretsiz kargo mevcut."

    if any(x in t for x in ["kaç günde", "kac gunde", "ne zaman gelir", "teslimat", "kaç gün", "kac gun"]):
        return "Siparişiniz ertesi gün hazırlanır. Teslimat ise ortalama 4 iş günü içerisinde gerçekleşmektedir 😊"

    if any(x in t for x in ["ödeme", "odeme", "shopier", "havale", "kapıda", "kapida"]):
        return "Ödeme seçeneklerimiz mevcut 😊 Havale/EFT, kapıda ödeme veya Shopier üzerinden güvenli ödeme yapabilirsiniz.\n\nShopier: www.shopier.com/kilifstorie"

    if any(x in t for x in ["tasarımları", "tasarimlari", "modelleri", "örnek", "ornek", "nereden bak", "görmek"]):
        return "Elbette 😊 Tasarımlarımızı Instagram profilimizden veya Shopier mağazamızdan inceleyebilirsiniz.\n\n🛍️ www.shopier.com/kilifstorie"

    return None

def gpt_reply(user_id, text, has_photo=False):
    user = get_user(user_id)

    if user["handoff"]:
        return None

    if has_photo:
        user["photo"] = True

    if detect_model(text):
        user["model"] = True

    if detect_design(text):
        user["design"] = True

    direct = known_answer(text)
    if direct:
        reply = direct
        handoff = False
    else:
        user["history"].append({"role": "user", "content": text})
        user["history"] = user["history"][-10:]

        durum = {
            "telefon_modeli_alindi": user["model"],
            "tasarim_istegi_alindi": user["design"],
            "foto_geldi": user["photo"],
            "bot_cevap_sayisi": user["bot_replies"]
        }

        conversation = f"Müşteri durumu: {json.dumps(durum, ensure_ascii=False)}\n\n"
        for msg in user["history"]:
            role = "Müşteri" if msg["role"] == "user" else "KilifStoria"
            conversation += f"{role}: {msg['content']}\n"

        if has_photo:
            conversation += "\nMüşteri fotoğraf/görsel gönderdi. Bunu dikkate al.\n"

        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=SYSTEM_PROMPT,
            input=conversation,
            max_output_tokens=220
        )

        raw = response.output_text.strip()
        print("GPT RAW:", raw, flush=True)

        try:
            parsed = json.loads(raw)
            reply = parsed.get("reply", "").strip()
            handoff = bool(parsed.get("handoff", False))
        except Exception:
            reply = raw
            handoff = False

    user["bot_replies"] += 1

    if user["model"] and user["design"]:
        handoff = True
        reply = "Harika 😊 Bilgileri aldım. Tasarım ve sipariş işlemi için ekip arkadaşımız birazdan size dönüş yapacak."

    if user["bot_replies"] >= 6:
        handoff = True
        reply = "Harika 😊 Bilgileri aldım. Tasarım ve sipariş işlemi için ekip arkadaşımız birazdan size dönüş yapacak."

    if handoff:
        user["handoff"] = True

    user["history"].append({"role": "assistant", "content": reply})
    user["history"] = user["history"][-10:]

    return reply

@app.route("/")
def home():
    return "<h1>Instagram Bot Çalışıyor!</h1><p>KilifStoria AI karşılama botu aktif.</p>"

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

    print("===== EVENT GELDİ / KILIFSTORIA AI V2 =====", flush=True)
    print(json.dumps(data, indent=4, ensure_ascii=False), flush=True)

    for entry in data.get("entry", []):
        for item in entry.get("messaging", []):
            sender_id = item.get("sender", {}).get("id")
            recipient_id = item.get("recipient", {}).get("id")
            message = item.get("message", {})

            if message.get("is_echo"):
                if recipient_id:
                    get_user(recipient_id)["handoff"] = True
                    print("Manuel cevap algılandı, müşteri bota kapatıldı.", flush=True)
                continue

            if sender_id in OWN_IDS:
                continue

            text = message.get("text", "")
            attachments = message.get("attachments", [])
            has_photo = bool(attachments)

            if sender_id and (text or has_photo):
                if not text and has_photo:
                    text = "Müşteri fotoğraf gönderdi."

                try:
                    reply = gpt_reply(sender_id, text, has_photo)
                    if reply:
                        send_message(sender_id, reply)
                except Exception as e:
                    print("BOT HATASI:", str(e), flush=True)
                    send_message(sender_id, "Merhaba 😊 Hangi telefon modeli için kılıf düşünüyorsunuz?")

    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)