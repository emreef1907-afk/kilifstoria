import re

PHONE_WORDS = [
    'iphone', 'samsung', 'xiaomi', 'redmi', 'oppo', 'tecno', 'realme', 'huawei',
    'honor', 'vivo', 'reeder', 'infinix', 'poco', 'galaxy', 'note', 'pro',
    'max', 'plus', 'mini', 's3', 's4', 's5', 'a10', 'a20', 'a30', 'a50', 'a55',
    'a54', 'a34', 's23', 's24', 's25'
]

DESIGN_WORDS = [
    'foto', 'fotoğraf', 'fotograf', 'resim', 'kendi foto', 'kendi resim',
    'isim', 'isimli', 'özel', 'ozel', 'sayfadaki', 'sayfanızdaki', 'tasarım',
    'tasarim', 'model beğendim', 'model begendim', 'bunu istiyorum',
    'bu olsun', 'aynısı', 'aynisi', 'logo', 'yazı', 'yazi'
]

NO_MORE_WORDS = [
    'yok', 'yoktur', 'tamam', 'olur', 'teşekkür', 'tesekkur', 'sağ ol',
    'sag ol', 'anladım', 'anladim', 'başka yok', 'baska yok', 'soru yok'
]

GREETING_WORDS = ['merhaba', 'selam', 'sa', 'slm', 'mrb', 'hello', 'hi']


def normalize(text: str) -> str:
    return (text or '').lower().strip()


def has_any(text: str, words) -> bool:
    t = normalize(text)
    return any(w in t for w in words)


def detect_phone_model(text: str) -> bool:
    t = normalize(text)
    if len(t) < 2:
        return False
    if has_any(t, PHONE_WORDS):
        return True
    # Tek başına iPhone numarası gibi yazımlar: "13", "15 pro" vb.
    if re.search(r'\b(iphone\s*)?(1[1-6]|xr|xs|se)\b', t):
        return True
    return False


def detect_design(text: str, has_photo: bool = False) -> bool:
    if has_photo:
        return True
    return has_any(text, DESIGN_WORDS)


def detect_no_more_questions(text: str) -> bool:
    return has_any(text, NO_MORE_WORDS)


def detect_intent(text: str):
    t = normalize(text)

    if any(x in t for x in ['telefonuma uygun', 'model yok', 'cihazım yok', 'cihazim yok', 'uygun model yok']):
        return 'model_missing'
    if any(x in t for x in ['fiyat', 'kaç', 'kac', 'ücret', 'ucret', 'tl', 'para']):
        return 'price'
    if any(x in t for x in ['kargo', 'hangi firma', 'ptt']):
        return 'cargo'
    if any(x in t for x in ['teslimat', 'kaç gün', 'kac gun', 'ne zaman gelir', 'kaç günde', 'kac gunde']):
        return 'delivery'
    if any(x in t for x in ['ödeme', 'odeme', 'shopier', 'havale', 'kapıda', 'kapida']):
        return 'payment'
    if any(x in t for x in ['kaliteli', 'baskı', 'baski', 'solma', 'silinir', 'çıkar', 'cikar', 'çıkma', 'cikma']):
        return 'quality'
    if any(x in t for x in ['tasarımları', 'tasarimlari', 'modelleri', 'nereden bak', 'görmek', 'ornek', 'örnek']):
        return 'designs'
    if any(x in t for x in ['yeriniz', 'nerede', 'konum', 'mağaza', 'magaza', 'adana']):
        return 'location'
    if any(x in t for x in ['dolandırıcı', 'dolandirici', 'güvenilir', 'guvenilir', 'sahte']):
        return 'trust'

    return None
