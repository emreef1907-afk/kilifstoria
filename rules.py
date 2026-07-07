import re

PHONE_BRANDS = [
    "iphone", "samsung", "xiaomi", "redmi", "oppo", "tecno",
    "realme", "huawei", "honor", "vivo", "infinix", "poco",
    "galaxy", "reeder", "general mobile", "gm"
]

DESIGN_WORDS = [
    "sayfadaki", "sayfanızdaki", "sayfanizdaki", "tasarım", "tasarim",
    "fotoğraf", "fotograf", "foto", "resim", "kendi fotoğrafım",
    "kendi fotografim", "isim", "isimli", "özel", "ozel"
]

def normalize(text: str) -> str:
    return (text or "").lower().strip()

def detect_phone_model(text: str) -> bool:
    t = normalize(text)
    if len(t) < 2:
        return False

    if any(b in t for b in PHONE_BRANDS):
        return True

    # iPhone modelleri bazen sadece "13", "14 pro" gibi yazılıyor
    if re.search(r"\b(11|12|13|14|15|16)\s*(pro|max|plus|promax)?\b", t):
        return True

    # Samsung A/S serileri
    if re.search(r"\b(a|s|m)\s?\d{2}\b", t):
        return True

    return False

def detect_design(text: str) -> bool:
    t = normalize(text)
    return any(w in t for w in DESIGN_WORDS) or t in {"1", "2", "3"}

def direct_answer(text: str) -> str | None:
    t = normalize(text)

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

    if any(x in t for x in ["teslimat", "kaç gün", "kac gun", "kaç günde", "kac gunde", "ne zaman gelir"]):
        return "Sipariş ertesi gün hazırlanır. Teslimat ortalama 4 iş günü içinde gerçekleşir 😊"

    if any(x in t for x in ["ödeme", "odeme", "shopier", "havale", "kapıda", "kapida"]):
        return (
            "Ödeme seçeneklerimiz mevcut 😊\n"
            "Havale/EFT, kapıda ödeme veya Shopier üzerinden güvenli ödeme yapabilirsiniz.\n\n"
            "Shopier: www.shopier.com/kilifstorie"
        )

    if any(x in t for x in ["telefonuma uygun", "model yok", "cihazım yok", "cihazim yok", "uygun model yok"]):
        return (
            "Hiç sorun değil 😊 Sayfamızdaki telefon modelleri sadece örnek tasarımdır. "
            "Beğendiğiniz tasarımı seçmeniz yeterli, biz tüm telefon marka ve modellerine uygun şekilde hazırlıyoruz."
        )

    if any(x in t for x in ["tasarımları", "tasarimlari", "modelleri", "örnekleri", "ornekleri", "nereden bak", "nereden bakabilirim"]):
        return (
            "Elbette 😊 Tasarımlarımızı Instagram profilimizden veya Shopier mağazamızdan inceleyebilirsiniz.\n\n"
            "🛍️ www.shopier.com/kilifstorie"
        )

    if any(x in t for x in ["solma", "silinme", "çıkar mı", "cikar mi", "baskı kalitesi", "baski kalitesi", "uv", "lazer"]):
        return (
            "Baskılarımız UV / Lazer UV baskı teknolojisi ile yapılır 😊 "
            "Normal kullanımda solma, silinme veya çıkma yapmaz."
        )

    return None

def update_state_from_text(user: dict, text: str, has_photo: bool):
    if has_photo:
        user["photo"] = True
        if not user["design"]:
            user["design"] = "Kendi fotoğrafı"

    if detect_phone_model(text) and not user["model"]:
        user["model"] = text.strip()

    if detect_design(text) and not user["design"]:
        t = normalize(text)
        if t == "1" or "sayfa" in t:
            user["design"] = "Sayfadaki tasarımlardan biri"
        elif t == "2" or "foto" in t or "resim" in t:
            user["design"] = "Kendi fotoğrafı"
        elif t == "3" or "isim" in t:
            user["design"] = "İsimli tasarım"
        else:
            user["design"] = text.strip()

def enough_to_handoff(user: dict) -> bool:
    return bool(user.get("model") and user.get("design"))
