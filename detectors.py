import re

MODEL_WORDS = [
    'iphone', 'samsung', 'galaxy', 'xiaomi', 'redmi', 'oppo', 'tecno', 'realme',
    'huawei', 'honor', 'vivo', 'reeder', 'infinix', 'poco', 'note', 'pro', 'max', 'plus', 'mini'
]
DESIGN_WORDS = [
    'foto', 'fotoğraf', 'fotograf', 'resim', 'kendi foto', 'isim', 'isimli',
    'özel', 'ozel', 'sayfadaki', 'tasarım', 'tasarim', 'bunu istiyorum', 'model beğendim', 'model begendim'
]
NO_MORE_WORDS = ['yok', 'yoktur', 'tamam', 'olur', 'teşekkür', 'tesekkur', 'sağ ol', 'sag ol', 'anladım', 'anladim']


def detect_model(text):
    t = (text or '').lower()
    if any(w in t for w in MODEL_WORDS):
        return True
    if re.search(r'\b(a|s|note)\s?\d{1,3}\b', t):
        return True
    return False


def detect_design(text):
    t = (text or '').lower()
    return any(w in t for w in DESIGN_WORDS)


def is_no_more_questions(text):
    t = (text or '').lower().strip()
    return any(w in t for w in NO_MORE_WORDS)


def quick_answer(text):
    t = (text or '').lower()
    if any(x in t for x in ['fiyat ne', 'ne kadar', 'kaç tl', 'kac tl', 'ücret ne', 'ucret ne', 'fiyatınız', 'fiyatiniz']):
        from knowledge import PRICE_TEXT
        return PRICE_TEXT
    if any(x in t for x in ['kargo', 'hangi firma', 'ptt']):
        return 'Gönderimlerimizi PTT Kargo ile sağlıyoruz 😊 81 ile ücretsiz kargo mevcut.'
    if any(x in t for x in ['teslimat', 'kaç gün', 'kac gun', 'ne zaman gelir', 'kaç günde', 'kac gunde']):
        return 'Sipariş ertesi gün hazırlanır. Teslimat ortalama 4 iş günü içinde gerçekleşir 😊'
    if any(x in t for x in ['ödeme', 'odeme', 'shopier', 'havale', 'kapıda', 'kapida']):
        return 'Ödeme seçeneklerimiz mevcut 😊 Havale/EFT, kapıda ödeme veya Shopier üzerinden güvenli ödeme yapabilirsiniz.\n\nShopier: www.shopier.com/kilifstorie'
    if any(x in t for x in ['kaliteli', 'baskı', 'baski', 'solma', 'silinir', 'çıkar', 'cikar']):
        return 'Evet 😊 Baskılarımız UV / Lazer UV baskı teknolojisi ile kılıfa işleniyor. Normal kullanımda solma, silinme veya çıkma olmaz.'
    if any(x in t for x in ['telefonuma uygun', 'model yok', 'cihazım yok', 'cihazim yok', 'uygun model yok']):
        return 'Hiç sorun değil 😊 Sayfamızdaki telefon modelleri sadece örnek tasarımdır. Beğendiğiniz tasarımı seçmeniz yeterli, biz tüm telefon marka ve modellerine uygun şekilde hazırlıyoruz.'
    if any(x in t for x in ['tasarımları', 'tasarimlari', 'modelleri', 'nereden bak', 'görmek', 'ornek', 'örnek']):
        return 'Elbette 😊 Tasarımlarımızı Instagram profilimizden veya Shopier mağazamızdan inceleyebilirsiniz.\n\n🛍️ www.shopier.com/kilifstorie'
    if any(x in t for x in ['yeriniz', 'nerede', 'konum', 'mağaza', 'magaza']):
        return "Adana'da hizmet veriyoruz 😊 Siparişleri PTT Kargo ile Türkiye'nin 81 iline ücretsiz gönderiyoruz."
    return None
