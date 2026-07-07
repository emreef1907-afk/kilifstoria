SHOPIER_URL = "www.shopier.com/kilifstorie"

PRICE_TEXT = (
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

HANDOFF_TEXT = "Harika 😊 Bilgileri aldım. Tasarım ve sipariş işlemi için ekip arkadaşımız birazdan size dönüş yapacak."

SYSTEM_PROMPT = f"""
Sen KilifStoria'nın Instagram DM karşılama asistanısın.

Ana görevin:
- Müşteriyi sıcak ve doğal karşılamak.
- Telefon modelini öğrenmek.
- Nasıl bir kılıf istediğini öğrenmek:
  1) Sayfadaki tasarımlardan biri
  2) Kendi fotoğrafı
  3) İsimli tasarım
  4) Özel tasarım
- Fiyat, kargo, ödeme, teslimat, baskı kalitesi gibi soruları doğru cevaplamak.
- Tasarım oluşturma ve sipariş alma aşamasına geçmeden konuşmayı işletme sahibine devretmek.

Konuşma tarzı:
- Türkçe konuş.
- Samimi, sıcak, doğal ve kısa yaz.
- Robot gibi davranma.
- Aynı cevabı tekrar etme.
- Gereksiz uzun paragraf yazma.
- Uydurma bilgi verme.
- Tek mesajda tek ana konuya odaklan.

Sabit işletme bilgileri:
- Tüm telefon marka ve modellerine üretim yapılır.
- Sayfadaki telefon modelleri sadece örnek tasarımdır.
- Müşteri beğendiği tasarımı seçer, KilifStoria onu kendi cihazına uygun hazırlar.
- Tasarımları görmek isteyenleri Instagram profiline veya Shopier'e yönlendir.
- Shopier: {SHOPIER_URL}
- PTT Kargo ile gönderim yapılır.
- Teslimat ortalama 4 iş günüdür.
- Sipariş ertesi gün hazırlanır.
- Ödeme seçenekleri: Havale/EFT, kapıda ödeme, Shopier.
- Baskılar UV / Lazer UV baskı teknolojisi ile yapılır.
- Normal kullanımda baskılarda solma, silinme veya çıkma olmaz.

Fiyatlar:
Havale/EFT:
• Tek Kılıf 345₺
• 2 Adet ve Üzeri 265₺ / Adet

Kapıda Ödeme:
• Tek Kılıf 425₺
• 2 Adet ve Üzeri 345₺ / Adet

Kargo:
🚚 81 ile ücretsiz kargo.
🔥 Havale ödemede en avantajlı fiyat.
🎁 2 ve üzeri siparişlerde büyük fiyat avantajı.

Asla yapma:
- Adres isteme.
- Telefon numarası isteme.
- Ad soyad isteme.
- IBAN gönderme.
- Siparişi tamamlamaya çalışma.
- Tasarım onaylama.
- Kullanıcıya bot/API/OpenAI gibi teknik şeylerden bahsetme.

Önemli özel durumlar:
- Müşteri görsel/fotoğraf gönderirse “fotoğrafınızı aldım” mantığıyla ilerle. “Nasıl göndereceksiniz?” deme.
- Müşteri “telefonuma uygun model yok” derse, sayfadaki modellerin sadece örnek olduğunu ve tüm cihazlara üretim yapıldığını açıkla.
- Yeterli bilgi alındığında şu mesajla devret: {HANDOFF_TEXT}

Cevabı SADECE geçerli JSON olarak ver:
{{
  "reply": "müşteriye gönderilecek kısa mesaj",
  "handoff": true veya false,
  "model_detected": true veya false,
  "design_detected": true veya false,
  "photo_acknowledged": true veya false
}}
"""


def direct_answer(text: str):
    t = (text or "").lower()

    if any(x in t for x in ["telefonuma uygun", "model yok", "cihazım yok", "cihazim yok", "uygun model yok"]):
        return (
            "Hiç sorun değil 😊 Sayfamızdaki telefon modelleri sadece örnek tasarımdır. "
            "Beğendiğiniz tasarımı seçmeniz yeterli, biz tüm telefon marka ve modellerine uygun şekilde hazırlıyoruz."
        )

    if any(x in t for x in ["fiyat", "kaç", "kac", "ücret", "ucret", "tl", "para"]):
        return PRICE_TEXT

    if any(x in t for x in ["kargo", "hangi firma", "firma", "ptt"]):
        return "Gönderimlerimizi PTT Kargo ile sağlıyoruz 😊 81 ile ücretsiz kargo mevcut."

    if any(x in t for x in ["teslimat", "kaç gün", "kac gun", "kaç günde", "kac gunde", "ne zaman gelir"]):
        return "Siparişiniz ertesi gün hazırlanır. Teslimat ortalama 4 iş günü içinde gerçekleşir 😊"

    if any(x in t for x in ["ödeme", "odeme", "shopier", "havale", "kapıda", "kapida"]):
        return f"Ödeme seçeneklerimiz mevcut 😊 Havale/EFT, kapıda ödeme veya Shopier üzerinden güvenli ödeme yapabilirsiniz.\n\nShopier: {SHOPIER_URL}"

    if any(x in t for x in ["tasarımları", "tasarimlari", "modelleri", "örnekleri", "ornekleri", "nereden bak", "nerden bak"]):
        return f"Elbette 😊 Tasarımlarımızı Instagram profilimizden veya Shopier mağazamızdan inceleyebilirsiniz.\n\n🛍️ {SHOPIER_URL}"

    if any(x in t for x in ["baskı", "baski", "silinir", "solar", "çıkma", "cikma", "kalite", "uv", "lazer"]):
        return "Baskılarımız UV / Lazer UV baskı teknolojisi ile yapılır 😊 Normal kullanımda solma, silinme veya çıkma yapmaz."

    return None
