from flask import Flask, request
from dotenv import load_dotenv
from openai import OpenAI
import os, json, requests

load_dotenv()
app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "emre123")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

IG_API = "https://graph.instagram.com/v25.0/me/messages"
MODEL = "gpt-4.1-mini"

OWN_IDS = {"17841465752722469", "27903058482613663"}

users = {}

SYSTEM_PROMPT = """
Sen KilifStoria'nın Instagram DM karşılama asistanısın.

Görevin:
- Müşteriyi sıcak ve doğal karşıla.
- Samimi sohbetle telefon modelini öğren.
- Nasıl bir kılıf/tasarım istediğini öğren:
  1) Sayfadaki tasarımlardan mı?
  2) Kendi fotoğrafıyla mı?
  3) İsimli / taclı özel tasarım mı?
- Müşterinin aklındaki soruları doğru bilgilerle cevapla.
- Tasarım oluşturma ve sipariş alma aşamasına geçme.
- Yeterli bilgi alınca sohbeti işletme sahibine devret ve sonra sus.

İşletme bilgileri:
- Tüm telefon marka ve modellerine üretim yapılır.
- Sayfadaki iPhone 15 gibi modeller sadece örnek tasarımdır.
- Müşteri sadece tasarımı seçer, biz kendi telefon modeline uygun hazırlarız.
- PTT Kargo ile gönderim yapılır.
- Teslimat ortalama 4 iş günü.
- Sipariş ertesi gün hazırlanır.
- Ödeme seçenekleri: Havale/EFT, kapıda ödeme, Shopier.
- Shopier: www.shopier.com/kilifstorie
- Tasarımları görmek isteyenleri Instagram profiline veya Shopier sayfasına yönlendir.

Fiyatlar:
Havale/EFT:
- Tek kılıf 345 TL
- 2 adet ve üzeri tanesi 265 TL

Kapıda ödeme:
- Tek kılıf 425 TL
- 2 adet ve üzeri tanesi 345 TL

Çok sık gelen soru:
Müşteri “telefonuma uygun model sayfanızda yok” derse:
“Sayfamızdaki modeller örnek tasarımdır. Tasarımı seçmeniz yeterli, biz tüm cihazlara uygun şekilde hazırlıyoruz.”

Konuşma tarzı:
- Türkçe konuş.
- Doğal, samimi, kısa yaz.
- Robot gibi davranma.
- Çok uzun paragraf yazma.
- Gereksiz emoji kullanma.
- Uydurma bilgi verme.
- Bilmediğin soruda: “Bunu ekip arkadaşımız net kontrol edip dönüş yapsın” de.
- Sipariş bilgisi isteme: ad, soyad, adres, telefon isteme.
- Tasarım/sipariş aşamasına gelince devret.

Devretme mesajı:
“Harika 😊 Bilgileri aldım. Tasarım ve sipariş işlemi için ekip arkadaşımız birazdan size dönüş yapacak.”

Cevabını SADECE JSON olarak ver:
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
        users[user_id] = {"history": [], "handoff": False}
    return users[user_id]

def gpt_reply(user_id, text):
    user = get_user(user_id)

    if user["handoff"]:
        return None

    user["history"].append({"role": "user", "content": text})
    user["history"] = user["history"][-12:]

    convo = ""
    for msg in user["history"]:
        who = "Müşteri" if msg["role"] == "user" else "KilifStoria"
        convo += f"{who}: {msg['content']}\n"

    response = client.responses.create(
        model=MODEL,
        instructions=SYSTEM_PROMPT,
        input=convo,
        max_output_tokens=250
    )

    raw = response.output_text.strip()
    print("GPT RAW:", raw, flush=True)

    try:
        data = json.loads(raw)
        reply = data.get("reply", "").strip()
        handoff = bool(data.get("handoff", False))
    except Exception:
        reply = raw
        handoff = False

    if not reply:
        reply = "Merhaba 😊 Hangi telefon modeli için kılıf düşünüyorsunuz?"

    user["history"].append({"role": "assistant", "content": reply})
    user["history"] = user["history"][-12:]

    if handoff:
        user["handoff"] = True

    return reply

@app.route("/")
def home():
    return "<h1>Instagram Bot Çalışıyor!</h1><p>KilifStoria GPT karşılama botu aktif.</p>"

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
    print("===== EVENT GELDİ / GPT KARŞILAMA =====", flush=True)
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
                try:
                    reply = gpt_reply(sender_id, text)
                    if reply:
                        send_message(sender_id, reply)
                except Exception as e:
                    print("GPT HATASI:", str(e), flush=True)
                    send_message(sender_id, "Merhaba 😊 Hangi telefon modeli için kılıf düşünüyorsunuz?")

    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)