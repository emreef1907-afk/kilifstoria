import re

MODEL_BRANDS = [
    "iphone", "samsung", "xiaomi", "redmi", "oppo", "tecno", "realme", "huawei",
    "honor", "vivo", "reeder", "infinix", "poco", "galaxy", "omix", "general mobile",
    "casper", "vestel", "gm", "note", "pro", "max", "plus", "mini", "blue max"
]

DESIGN_WORDS = [
    "foto", "fotoğraf", "fotograf", "resim", "kendi foto", "görsel", "gorsel",
    "isim", "isimli", "özel", "ozel", "sayfadaki", "tasarım", "tasarim",
    "bunu istiyorum", "bu resim", "bu görsel", "model beğendim", "model begendim"
]

NO_MORE_WORDS = [
    "yok", "yoktur", "tamam", "olur", "teşekkür", "tesekkur", "sağ ol", "sag ol",
    "anladım", "anladim", "şimdilik yok", "simdilik yok", "tamamdır", "tamamdir"
]

ORDER_WORDS = ["sipariş", "siparis", "alacağım", "alacagim", "verelim", "vericem", "istiyorum", "olsun"]


def normalize(text: str) -> str:
    return (text or "").lower().strip()


def detect_model(text: str):
    t = normalize(text)
    if not t:
        return None
    if any(word in t for word in MODEL_BRANDS):
        return text.strip()
    # S3 mini, A55, 15 pro gibi kısa model ifadeleri
    if re.search(r"\b([a-z]{1,3}\s?\d{1,3}|\d{2}\s?(pro|max|plus|mini)?)\b", t):
        return text.strip()
    return None


def detect_design(text: str, has_photo: bool = False):
    if has_photo:
        return "kendi fotoğrafı"
    t = normalize(text)
    if any(word in t for word in DESIGN_WORDS):
        if "isim" in t:
            return "isimli tasarım"
        if "foto" in t or "resim" in t or "görsel" in t or "gorsel" in t:
            return "kendi fotoğrafı"
        if "sayfa" in t or "model" in t or "tasarım" in t or "tasarim" in t:
            return "sayfadaki tasarım / özel tasarım"
        return text.strip()
    return None


def is_price_question(text: str) -> bool:
    t = normalize(text)
    if any(phrase in t for phrase in ["fiyat", "ücret", "ucret", "ne kadar", "kaç tl", "kac tl", "kaç para", "kac para"]):
        return True
    # Sadece kaç gün / kaç günde fiyat değildir.
    return False


def is_delivery_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in ["kaç günde", "kac gunde", "kaç gün", "kac gun", "ne zaman gelir", "teslimat", "hızlı kargo", "hizli kargo"])


def is_cargo_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in ["kargo", "hangi firma", "ptt"])


def is_payment_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in ["ödeme", "odeme", "shopier", "havale", "kapıda", "kapida", "kart"])


def is_quality_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in ["kaliteli", "kalite", "baskı", "baski", "solma", "silinir", "çıkar", "cikar", "uv"])


def is_model_missing_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in ["telefonuma uygun", "model yok", "cihazım yok", "cihazim yok", "uygun model yok"])


def is_design_gallery_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in ["tasarımları", "tasarimlari", "modelleri", "nereden bak", "görmek", "ornek", "örnek", "site", "link"])


def is_location_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in ["yeriniz", "nerede", "konum", "mağaza", "magaza", "hangi şehir", "hangi sehir"])


def is_trust_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in ["dolandırıcı", "dolandirici", "güvenilir", "guvenilir", "sahte", "emin miyim"])


def is_no_more_questions(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in NO_MORE_WORDS)


def is_order_intent(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in ORDER_WORDS)


SHOPIER_WORDS=[
"örnek","ornek","tasarım","tasarim","model","bak","bakabilir","görebilir","gorebilir",
"site","internet","link","shopier","karar veremedim","kararsız","kararsiz"
]

def wants_shopier(text:str)->bool:
    t=text.lower()
    return any(w in t for w in SHOPIER_WORDS)
