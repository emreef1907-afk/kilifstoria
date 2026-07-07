SHOP_NAME = 'KilifStoria'
LOCATION = 'Adana'
SHOPIER_URL = 'www.shopier.com/kilifstorie'
CARGO_COMPANY = 'PTT Kargo'
DELIVERY = 'Ortalama 4 iş günü'
PREPARATION = 'Siparişler ertesi gün hazırlanır'
FREE_SHIPPING = 'Türkiye’nin 81 iline ücretsiz kargo'

PRICES_TEXT = '''Fiyatlarımız şöyle 😊

💸 Havale / EFT
• Tek Kılıf 345₺
• 2 Adet ve Üzeri 265₺ / Adet

💸 Kapıda Ödeme
• Tek Kılıf 425₺
• 2 Adet ve Üzeri 345₺ / Adet

🚚 81 ile ücretsiz kargo.
🔥 Havale ödemede en avantajlı fiyat.
🎁 2 ve üzeri siparişlerde büyük fiyat avantajı.'''

HANDOFF_MESSAGE = 'Tasarım ve sipariş işlemi için ekip arkadaşımız birazdan size dönüş yapacak.'

BUSINESS_FACTS = f'''
İşletme: {SHOP_NAME}
Hizmet yeri: {LOCATION}
Kargo: {CARGO_COMPANY}
Gönderim: {FREE_SHIPPING}
Hazırlık: {PREPARATION}
Teslimat: {DELIVERY}
Ödeme seçenekleri: Havale/EFT, kapıda ödeme, Shopier
Shopier: {SHOPIER_URL}

Telefon ve tasarım bilgisi:
- Tüm telefon marka ve modellerine üretim yapılır.
- Sayfadaki telefon modelleri sadece örnek tasarımdır.
- Müşteri beğendiği tasarımı seçer; tasarım kendi cihazına uygun hazırlanır.
- Tasarım türleri: sayfadaki tasarımlardan biri, kendi fotoğrafı, isimli tasarım, özel tasarım.

Baskı kalitesi:
- Baskılar UV / Lazer UV baskı teknolojisi ile kılıfa işlenir.
- Normal kullanımda solma, silinme veya çıkma olmaz.
- Uzun ömürlü baskı kullanılır.

Fiyatlar:
{PRICES_TEXT}
'''

DIRECT_ANSWERS = {
    'price': PRICES_TEXT,
    'cargo': 'Gönderimlerimizi PTT Kargo ile sağlıyoruz 😊 81 ile ücretsiz kargo mevcut.',
    'delivery': 'Siparişler ertesi gün hazırlanır. Teslimat ortalama 4 iş günü içinde gerçekleşir 😊',
    'payment': f'Ödeme seçeneklerimiz mevcut 😊 Havale/EFT, kapıda ödeme veya Shopier üzerinden güvenli ödeme yapabilirsiniz.\n\nShopier: {SHOPIER_URL}',
    'quality': 'Evet 😊 Baskılarımız UV / Lazer UV baskı teknolojisi ile kılıfa işleniyor. Normal kullanımda solma, silinme veya çıkma olmaz.',
    'model_missing': 'Hiç sorun değil 😊 Sayfamızdaki telefon modelleri sadece örnek tasarımdır. Beğendiğiniz tasarımı seçmeniz yeterli, biz tüm telefon marka ve modellerine uygun şekilde hazırlıyoruz.',
    'designs': f'Elbette 😊 Tasarımlarımızı Instagram profilimizden veya Shopier mağazamızdan inceleyebilirsiniz.\n\n🛍️ {SHOPIER_URL}',
    'location': 'Adana’da hizmet veriyoruz 😊 Siparişleri PTT Kargo ile Türkiye’nin 81 iline ücretsiz gönderiyoruz.',
    'trust': 'Bunu sormanız çok normal 😊 Ödemeyi Shopier, havale/EFT veya kapıda ödeme ile yapabilirsiniz. Ayrıca siparişlerde PTT Kargo ile gönderim sağlıyoruz.',
}
