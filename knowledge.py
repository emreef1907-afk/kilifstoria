BUSINESS = {
    "name": "KilifStoria",
    "city": "Adana",
    "cargo_company": "PTT Kargo",
    "free_shipping": "81 ile ücretsiz kargo",
    "preparation_time": "Sipariş ertesi gün hazırlanır",
    "delivery_time": "Teslimat ortalama 4 iş günü içinde gerçekleşir",
    "shopier": "www.shopier.com/kilifstorie",
    "print_tech": "UV / Lazer UV baskı",
    "print_quality": "Normal kullanımda solma, silinme veya çıkma olmaz",
}

PRICES = {
    "havale_single": "345₺",
    "havale_multi": "265₺ / Adet",
    "cod_single": "425₺",
    "cod_multi": "345₺ / Adet",
}

HANDOFF_MESSAGE = "Tasarım ve sipariş işlemi için ekip arkadaşımız birazdan size dönüş yapacak."

PRICE_TEXT = f"""Fiyatlarımız şöyle 😊

💸 Havale / EFT
• Tek Kılıf {PRICES['havale_single']}
• 2 Adet ve Üzeri {PRICES['havale_multi']}

💸 Kapıda Ödeme
• Tek Kılıf {PRICES['cod_single']}
• 2 Adet ve Üzeri {PRICES['cod_multi']}

🚚 81 ile ücretsiz kargo.
🔥 Havale ödemede en avantajlı fiyat."""

FAQ = {
    "cargo": "Gönderimlerimizi PTT Kargo ile sağlıyoruz 😊 81 ile ücretsiz kargo mevcut.",
    "delivery": "Sipariş ertesi gün hazırlanır. Teslimat ortalama 4 iş günü içinde gerçekleşir 😊",
    "payment": "Ödeme seçeneklerimiz mevcut 😊 Havale/EFT, kapıda ödeme veya Shopier üzerinden güvenli ödeme yapabilirsiniz.\n\nShopier: www.shopier.com/kilifstorie",
    "quality": "Evet 😊 Baskılarımız UV / Lazer UV baskı teknolojisi ile kılıfa işleniyor. Normal kullanımda solma, silinme veya çıkma olmaz.",
    "model_missing": "Hiç sorun değil 😊 Sayfamızdaki telefon modelleri sadece örnek tasarımdır. Beğendiğiniz tasarımı seçmeniz yeterli, biz tüm telefon marka ve modellerine uygun şekilde hazırlıyoruz.",
    "designs": "Elbette 😊 Tasarımlarımızı Instagram profilimizden veya Shopier mağazamızdan inceleyebilirsiniz.\n\n🛍️ www.shopier.com/kilifstorie",
    "location": "Adana'da hizmet veriyoruz 😊 Siparişleri PTT Kargo ile Türkiye'nin 81 iline ücretsiz gönderiyoruz.",
    "trust": "Bunu sormanız çok normal 😊 Ödeme için Shopier, havale/EFT ve kapıda ödeme seçeneklerimiz mevcut. Baskılarımız UV baskı olduğu için normal kullanımda solma veya silinme yapmaz.",
}

FORBIDDEN_INTENTS = [
    "adres isteme",
    "telefon numarası isteme",
    "ad soyad isteme",
    "ödeme isteme",
    "iban verme",
    "sipariş alma",
]


SHOPIER_RULES = '''
###############################
SHOPIER KURALI (ÇOK ÖNEMLİ)
###############################
Müşteri örnek görmek, tasarım seçmek, model bakmak, site veya link istemek, karar verememek gibi ifadeler kullanırsa "Instagram sayfamıza bakın" deme.
Her zaman şu cevabı tercih et:

Tabii 😊 Örnek tasarımlarımızı buradan inceleyebilirsiniz:

🛍️ www.shopier.com/kilifstorie

Oradaki telefon modelleri sadece örnek tasarımdır. Beğendiğiniz tasarımı tüm telefon marka ve modellerine uygun hazırlıyoruz.
Beğendiğiniz tasarımın ekran görüntüsünü bize göndermeniz yeterli.
'''


SYSTEM_PROMPT = f'''
{SHOPIER_RULES}

ÇOK ÖNEMLİ:
- Müşteri "nasıl bakacağım", "hangi sayfadan", "site", "link", "örnek göster", "tasarımları nereden görebilirim" derse ASLA "Instagram sayfamıza bakabilirsiniz" deme.
- Doğrudan Shopier bağlantısını paylaş.
- Shopier linkini paylaşmaktan çekinme.
- Müşteri tasarım seçemiyorsa önce Shopier'e yönlendir.
'''
