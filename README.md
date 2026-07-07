# KilifStoria AI FINAL

Modüler Instagram DM karşılama botu.

## Dosyalar
- `app.py`: Flask webhook ve routing
- `instagram.py`: Instagram mesaj gönderimi
- `assistant.py`: GPT ve konuşma akışı
- `knowledge.py`: fiyat, kargo, ödeme, baskı bilgileri
- `detectors.py`: niyet/model/tasarım algılama
- `memory.py`: müşteri hafızası, MID ve echo kontrolü
- `config.py`: ortam değişkenleri

## Render Environment
Aşağıdaki değişkenler gerekli:
- `ACCESS_TOKEN`
- `VERIFY_TOKEN`
- `OPENAI_API_KEY`

Opsiyonel:
- `OPENAI_MODEL` varsayılan: `gpt-4.1-mini`
- `MAX_BOT_REPLIES` varsayılan: `5`

## Önemli güvenlik
- Aynı mesaja tek cevap verir.
- Botun kendi echo mesajını manuel cevap sanmaz.
- Sen manuel yazınca müşteride bot susar.
- Maksimum 5 otomatik cevap sonrası devreder.
