from flask import Flask, request
import os, json
from config import VERIFY_TOKEN
from memory import processed_mids, bot_sent_mids, remember_incoming, get_user
from instagram import send_message
from assistant import create_reply

app = Flask(__name__)


@app.route('/')
def home():
    return '<h1>Instagram Bot Çalışıyor!</h1><p>KilifStoria AI Brain aktif.</p>'


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
    data = request.json
    print('===== EVENT GELDİ / KILIFSTORIA AI BRAIN =====', flush=True)
    print(json.dumps(data, indent=4, ensure_ascii=False), flush=True)

    for entry in data.get('entry', []):
        for item in entry.get('messaging', []):
            sender_id = item.get('sender', {}).get('id')
            recipient_id = item.get('recipient', {}).get('id')
            message = item.get('message', {})
            mid = message.get('mid')

            if mid and mid in processed_mids:
                print('Aynı MID tekrar geldi, atlandı.', flush=True)
                continue
            if mid:
                processed_mids.add(mid)

            if message.get('is_echo'):
                if mid in bot_sent_mids:
                    print('Botun kendi echo mesajı atlandı.', flush=True)
                    continue
                if recipient_id:
                    get_user(recipient_id)['handoff'] = True
                    print(f'Manuel cevap algılandı. {recipient_id} için bot susturuldu.', flush=True)
                continue

            text = message.get('text', '')
            attachments = message.get('attachments', [])
            has_photo = bool(attachments)
            if not text and has_photo:
                text = 'Müşteri fotoğraf gönderdi.'

            if sender_id and (text or has_photo):
                if not remember_incoming(sender_id, text):
                    print('Aynı içerik yakın zamanda geldi, atlandı.', flush=True)
                    continue
                try:
                    reply = create_reply(sender_id, text, has_photo)
                    if reply:
                        send_message(sender_id, reply)
                except Exception as e:
                    print('BOT HATASI:', str(e), flush=True)
                    send_message(sender_id, 'Merhaba 😊 Hangi telefon modeli için kılıf düşünüyorsunuz?')

    return 'EVENT_RECEIVED', 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
