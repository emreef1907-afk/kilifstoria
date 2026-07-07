import re
from knowledge import PRICE_TEXT, SHOPIER_URL

MODEL_WORDS = [
    "iphone", "samsung", "xiaomi", "redmi", "oppo", "tecno", "realme",
    "huawei", "honor", "vivo", "infinix", "poco", "reeder", "galaxy",
]

DESIGN_WORDS = [
    "foto", "fotoğraf", "fotograf", "resim", "kendi", "isim", "isimli",
    "özel", "ozel", "sayfadaki", "tasarım", "tasarim", "model", "renk",
]

NO_MORE_WORDS = ["yok", "tamam", "sağol", "sagol", "teşekkür", "tesekkur", "olur", "ok", "eyvallah"]


def normalize(text: str) -> str:
    return (text or "").lower().strip()


def has_phone_model(text: str) -> bool:
    t = normalize(text)
    if any(w in t for w in MODEL_WORDS):
        return True
    # iPhone 13 gibi kısa model cevapları için: yalnızca rakam/pro/max/a55 vb.
    if re.search(r"\b(1[1-6]|[as]\d{2}|s2[0-9]|note\s?\d+|pro|max|plus)\b", t):
        return True
    return False


def has_design(text: str) -> bool:
    t = normalize(text)
    return any(w in t for w in DESIGN_WORDS) or t in {"1", "2", "3", "4"}


def no_more_questions(text: str) -> bool:
    t = normalize(text)
    return any(w in t for w in NO_MORE_WORDS) and len(t) <= 40


def direct_answer(text: str) -> str | None:
    t = normalize(text)

    if any(x in t for x in ["fiyat", "kaç", "kac", "ücret", "ucret", "tl", "para"]):
        return PRICE_TEXT

    if any(x in t for x in ["kargo", "hangi firma", "firma", "ptt"]):
        return "Gönderimlerimizi PTT Kargo ile sağlıyoruz 😊 81 ile ücretsiz kargo mevcut."

    if any(x in t for x in ["teslimat", "kaç gün", "kac gun", "ne zaman gelir", "kaç günde", "kac gunde"]):
        return "Siparişiniz ertesi gün hazırlanır. Teslimat ortalama 4 iş günü içinde gerçekleşir 😊"

    if any(x in t for x in ["ödeme", "odeme", "shopier", "havale", "kapıda", "kapida"]):
        return f"Ödeme seçeneklerimiz mevcut 😊 Havale/EFT, kapıda ödeme veya Shopier üzerinden güvenli ödeme yapabilirsiniz.\n\nShopier: {SHOPIER_URL}"

    if any(x in t for x in ["telefonuma uygun", "model yok", "cihazım yok", "cihazim yok", "uygun model yok"]):
        return "Hiç sorun değil 😊 Sayfamızdaki telefon modelleri sadece örnek tasarımdır. Beğendiğiniz tasarımı seçmeniz yeterli, biz tüm telefon marka ve modellerine uygun şekilde hazırlıyoruz."

    if any(x in t for x in ["tasarımları", "tasarimlari", "modelleri", "örnekleri", "ornekleri", "nereden bak", "görmek", "goreyim"]):
        return f"Elbette 😊 Tasarımlarımızı Instagram profilimizden veya Shopier mağazamızdan inceleyebilirsiniz.\n\n🛍️ {SHOPIER_URL}"

    if any(x in t for x in ["baskı", "baski", "silinir", "solar", "solma", "çıkar", "cikar", "kaliteli", "uv", "lazer"]):
        return "Baskılarımız UV (Lazer UV) baskı teknolojisi ile kılıflara işleniyor 😊 Normal kullanımda solma, silinme veya çıkma yapmaz."

    if any(x in t for x in ["nerede", "yeriniz", "konum", "mağaza", "magaza", "şehir", "sehir"]):
        return "Adana'da hizmet veriyoruz 😊 Siparişlerimizi PTT Kargo ile Türkiye'nin 81 iline ücretsiz gönderiyoruz."

    return None
