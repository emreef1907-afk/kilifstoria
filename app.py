from flask import Flask, request
import json

from config import VERIFY_TOKEN, PORT
from instagram import send_message
from assistant import create_reply
from memory import (
    is_processed,
    mark_processed,
    start_processing,
    finish_processing,
    is_bot_sent,
    set_handoff,
)

app = Flask(__name__)


@app.route('/')
def home():
    return '<h1>Instagram Bot Çalışıyor!</h1><p>KilifStoria AI FINAL aktif.</p>'


@app.route('/privacy')
def privacy():
    return '<h1>KilifStoria Gizlilik Politikası</h1><p>Veri silme talepleri: emrelaydn02@gmail.com</p>'


@app.route('/terms')
def terms():
    return '<h1>KilifStoria Hizmet Şartları</h1><p>KilifStoria otomatik mesaj botu.</p>'


@app.route('/data-deletion')
def data_deletion():
    return '<h1>Veri Silme Talimatları</h1><p>Veri silme talepleri: emrelaydn02@gmail.com</p>'


@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge'), 200
    return 'Forbidden', 403


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json or {}
    print('===== EVENT GELDİ / KILIFSTORIA AI FINAL =====', flush=True)
    print(json.dumps(data, indent=4, ensure_ascii=False), flush=True)

    for entry in data.get('entry', []):
        for item in entry.get('messaging', []):
            sender_id = item.get('sender', {}).get('id')
            recipient_id = item.get('recipient', {}).get('id')
            message = item.get('message', {}) or {}
            mid = message.get('mid')

            # Aynı mesajı ikinci kez asla işleme.
            if mid and is_processed(mid):
                print('Aynı MID tekrar geldi, atlandı:', mid, flush=True)
                continue

            if mid and not start_processing(mid):
                print('MID şu an işleniyor, atlandı:', mid, flush=True)
                continue

            try:
                # Echo: hesap tarafından çıkan mesaj.
                # Bot kendi gönderdiği mesajı echo olarak alırsa susturma.
                # Botun gönderdiği MID değilse, bu manuel cevaptır; müşteride botu sustur.
                if message.get('is_echo'):
                    if mid and is_bot_sent(mid):
                        print('Botun kendi echo mesajı atlandı:', mid, flush=True)
                    else:
                        if recipient_id:
                            set_handoff(recipient_id, True)
                            print(f'Manuel cevap algılandı. {recipient_id} için bot susturuldu.', flush=True)
                    if mid:
                        mark_processed(mid)
                    continue

                text = message.get('text', '') or ''
                attachments = message.get('attachments', []) or []
                has_photo = bool(attachments)

                if not sender_id or not (text or has_photo):
                    if mid:
                        mark_processed(mid)
                    continue

                if not text and has_photo:
                    text = 'Müşteri fotoğraf gönderdi.'

                reply = create_reply(sender_id, text, has_photo)
                if reply:
                    send_message(sender_id, reply)

                if mid:
                    mark_processed(mid)

            except Exception as exc:
                print('WEBHOOK/BOT HATASI:', str(exc), flush=True)
                try:
                    if sender_id:
                        send_message(sender_id, 'Merhaba 😊 Hangi telefon modeli için kılıf düşünüyorsunuz?')
                except Exception as send_exc:
                    print('HATA MESAJI GÖNDERİLEMEDİ:', str(send_exc), flush=True)
                if mid:
                    mark_processed(mid)
            finally:
                finish_processing(mid)

    return 'EVENT_RECEIVED', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
