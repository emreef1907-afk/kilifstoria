from flask import Flask, request
from dotenv import load_dotenv
import os, json, time

load_dotenv()

from config import VERIFY_TOKEN, OWN_IDS, MAX_BOT_REPLIES_PER_USER, MIN_SECONDS_BETWEEN_REPLIES
from detectors import detect_model, detect_design
from gpt import generate_reply
from instagram import send_message
from knowledge import direct_answer, HANDOFF_TEXT
from memory import (
    get_user, remember_mid, is_bot_echo, can_reply, lock_user, unlock_user,
    mark_handoff, add_history, increment_reply
)

app = Flask(__name__)


def should_skip_echo(item, message):
    """Bot echo'su sadece atlanır; manuel echo müşteriyi kapatır."""
    if not message.get("is_echo"):
        return False

    mid = message.get("mid")
    recipient_id = item.get("recipient", {}).get("id")

    if is_bot_echo(mid):
        print("Botun kendi echo mesajı atlandı.", flush=True)
        return True

    # Eğer echo botun gönderdiği kayıtlı bir mid değilse bunu manuel cevap kabul ediyoruz.
    if recipient_id:
        mark_handoff(recipient_id)
        print("Manuel cevap algılandı, bu müşteri için bot susturuldu.", flush=True)

    return True


def prepare_reply(user_id: str, text: str, has_photo: bool):
    user = get_user(user_id)

    if user["handoff"]:
        print("Kullanıcı handoff durumunda, cevap yok.", flush=True)
        return None

    if user["bot_replies"] >= MAX_BOT_REPLIES_PER_USER:
        mark_handoff(user_id)
        print("Maksimum bot cevabı doldu, cevap yok.", flush=True)
        return None

    now = time.time()
    if now - user["last_reply_time"] < MIN_SECONDS_BETWEEN_REPLIES:
        print("Çok hızlı tekrar mesaj geldi, spam koruması nedeniyle cevap yok.", flush=True)
        return None

    if has_photo:
        user["photo"] = True
        user["design"] = True

    if detect_model(text):
        user["model"] = True

    if detect_design(text, has_photo):
        user["design"] = True

    # Bazı sabit sorular GPT'ye gitmeden cevaplanır. Daha ucuz ve daha güvenli.
    direct = direct_answer(text)
    if direct:
        reply = direct
        handoff = False
    else:
        add_history(user_id, "user", text)
        result = generate_reply(user, text, has_photo)
        reply = result["reply"]
        handoff = result["handoff"]
        if result.get("model_detected"):
            user["model"] = True
        if result.get("design_detected"):
            user["design"] = True
        if result.get("photo_acknowledged"):
            user["photo"] = True

    # Bilgiler tamamlandıysa devret.
    if user["model"] and user["design"]:
        reply = HANDOFF_TEXT
        handoff = True

    # Son cevap hakkıysa da devret.
    if user["bot_replies"] + 1 >= MAX_BOT_REPLIES_PER_USER:
        reply = HANDOFF_TEXT
        handoff = True

    increment_reply(user_id)
    add_history(user_id, "assistant", reply)

    if handoff:
        mark_handoff(user_id)

    return reply


@app.route("/")
def home():
    return "<h1>Instagram Bot Çalışıyor!</h1><p>KilifStoria AI V3 aktif.</p>"


@app.route("/privacy")
def privacy():
    return """
    <h1>KilifStoria Gizlilik Politikası</h1>
    <p>KilifStoria, Instagram üzerinden gelen müşteri mesajlarını yanıtlamak ve sipariş öncesi destek sağlamak amacıyla Meta Instagram API kullanır.</p>
    <p>Toplanan veriler: Instagram kullanıcı ID, mesaj içeriği ve mesaj zamanı.</p>
    <p>Bu veriler üçüncü kişilerle satılmaz veya paylaşılmaz.</p>
    <p>Veri silme talepleri için: <b>emrelaydn02@gmail.com</b></p>
    """


@app.route("/terms")
def terms():
    return """
    <h1>KilifStoria Hizmet Şartları</h1>
    <p>Bu uygulama, Instagram mesajlarına otomatik ön karşılama ve destek cevabı vermek amacıyla kullanılır.</p>
    <p>Bot sipariş tamamlamaz, ödeme almaz ve müşteri bilgisi toplamaz. Tasarım ve sipariş işlemleri işletme sahibi tarafından yürütülür.</p>
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
            message = item.get("message", {})

            if should_skip_echo(item, message):
                continue

            if sender_id in OWN_IDS:
                print("Kendi hesap ID'sinden gelen mesaj atlandı.", flush=True)
                continue

            mid = message.get("mid")
            if not remember_mid(mid):
                print("Aynı MID tekrar geldi, cevap verilmedi.", flush=True)
                continue

            text = message.get("text", "")
            attachments = message.get("attachments", [])
            has_photo = bool(attachments)

            if not sender_id or not (text or has_photo):
                continue

            if not can_reply(sender_id):
                print("Kullanıcıya cevap verilmeyecek durumda.", flush=True)
                continue

            if not lock_user(sender_id):
                print("Bu kullanıcı zaten işleniyor, tekrar cevap yok.", flush=True)
                continue

            try:
                if not text and has_photo:
                    text = "Müşteri fotoğraf gönderdi."

                reply = prepare_reply(sender_id, text, has_photo)
                if reply:
                    # Robot gibi anında basmamak için küçük bekleme.
                    time.sleep(2)
                    send_message(sender_id, reply)
            except Exception as exc:
                print("BOT HATASI:", str(exc), flush=True)
                try:
                    send_message(sender_id, "Merhaba 😊 Hangi telefon modeli için kılıf düşünüyorsunuz?")
                except Exception as send_exc:
                    print("HATA MESAJI GÖNDERİLEMEDİ:", str(send_exc), flush=True)
            finally:
                unlock_user(sender_id)

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
