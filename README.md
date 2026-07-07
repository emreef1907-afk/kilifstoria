# KilifStoria AI V4

Bu sürüm, konuşmada belirlenen tüm kurallara göre hazırlandı:

- Aynı `mid` sadece 1 kez işlenir.
- Aynı içerik kısa sürede tekrar gelirse cevap verilmez.
- Aynı cevap kısa sürede tekrar gönderilmez.
- Bot kendi echo mesajında susmaz.
- Emre manuel yazarsa bot o müşteride susar.
- Cevaplar 8-15 saniye gecikmeli gönderilir.
- Mesaj sınırı yoktur; bot müşteri hazır olunca devreder.
- Sipariş almaz, adres/telefon/ad-soyad istemez.
- Kapanış mesajı sadece: `Tasarım ve sipariş işlemi için ekip arkadaşımız birazdan size dönüş yapacak.`

## Dosyalar

- `app.py`: Flask webhook ve Meta event yönetimi
- `assistant.py`: GPT karar motoru ve konuşma akışı
- `detectors.py`: niyet/model/tasarım algılama
- `guard.py`: yasak cevap denetleyici
- `instagram.py`: Instagram mesaj gönderme
- `knowledge.py`: firma bilgileri ve fiyatlar
- `memory.py`: müşteri hafızası ve spam koruması
- `config.py`: ayarlar

## Kurulum

`.env` dosyanızda şunlar olmalı:

```env
VERIFY_TOKEN=emre123
ACCESS_TOKEN=IGAA...
OPENAI_API_KEY=sk-proj-...
```

Deploy:

```powershell
git add .
git commit -m "kilifstoria ai v4"
git push
```
