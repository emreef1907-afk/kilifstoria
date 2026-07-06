from flask import Flask, request
from dotenv import load_dotenv
import os, json, requests, time
from openai import OpenAI

load_dotenv()
app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "emre123")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

IG_API = "https://graph.instagram.com/v25.0/me/messages"

OWN_IDS = {
    "17841465752722469",
    "27903058482613663"
}

memory = {}

SYSTEM_PROMPT = """
Sen KilifStoria'nın Instagram satış danışmanısın.

Tarzın:
- Türkçe konuş.
- Samimi, doğal, kısa ve satış odaklı ol.
- Robot gibi uzun uzun yazma.
- Gereksiz resmi konuşma.
- Müşteriyi sıkmadan siparişe yönlendir.
- Emojileri az ve doğal kullan.
- Aynı cevabı tekrar etme.

İşletme bilgileri:
- KilifStoria telefon kılıfı satıyor.
- Tüm telefon markaları ve modelleri için üretim yapılabiliyor.
- Kişiye özel baskı yapılabiliyor.
- Müşteri fotoğraf gönderebilir.
- Türkiye'nin 81 iline ücretsiz kargo var.

Fiyatlar:
Havale/EFT:
- Tek kılıf 345 TL
- 2 adet ve üzeri tanesi 265 TL

Kapıda ödeme:
- Tek kılıf 425 TL
- 2 adet ve üzeri tanesi 345 TL

Satış akışı:
1. İlk mesajda sıcak karşıla.
2. Telefon modelini öğren.
3. Tasarım/fotoğraf iste.
4. Fiyat sorarsa fiyatı net söyle.
5. Sipariş istiyorsa ad, soyad, telefon, açık adres ve ödeme tercihini iste.
6. Emin olmayan müşteriyi nazikçe yönlendir.
7. Bilmediğin konuda uydurma, “bunu ekip kontrol edip net bilgi verebilir” de.

Asla:
- Çok uzun paragraf yazma.
- Müşteriye aynı soruyu tekrar tekrar sorma.
- OpenAI, API, bot, sistem gibi teknik şeylerden bahsetme.
"""

def send_message(recipient_id, text):
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text[:950]}
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    r = requests.post(IG_API, headers=headers, json=payload)

    print("===== MESAJ GÖNDERME SONUCU =====", flush=True)
    print(r.status_code, flush=True)
    print(r.text, flush=True)


def gpt_cevap_uret(user_id, text):
    if user_id not in memory:
        memory[user_id] = []

    memory[user_id].append({"role": "user", "content": text})
    memory[user_id] = memory[user_id][-12:]

    conversation = ""
    for msg in memory[user_id]:
        role = "Müşteri" if msg["role"] == "user" else "KilifStoria"
        conversation += f"{role}: {msg['content']}\n"

    response = client.responses.create(
        model="gpt-5.4-mini",
        instructions=SYSTEM_PROMPT,
        input=conversation,
        max_output_tokens=220
    )

    cevap = response.output_text.strip()

    memory[user_id].append({"role": "assistant", "content": cevap})
    memory[user_id] = memory[user_id][-12:]

    return cevap


@app.route("/")
def home():
    return "<h1>Instagram Bot Çalışıyor!</h1><p>KilifStoria GPT satış botu aktif.</p>"


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

    print("===== YENİ EVENT GELDİ / GPT BOT =====", flush=True)
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
                try:
                    cevap = gpt_cevap_uret(sender_id, text)
                    send_message(sender_id, cevap)
                except Exception as e:
                    print("GPT HATASI:", str(e), flush=True)
                    send_message(sender_id, "Şu an kısa bir yoğunluk var 😊 Telefon modelinizi yazarsanız hemen yardımcı olalım.")

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)