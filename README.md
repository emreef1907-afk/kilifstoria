# KilifStoria AI FINAL SPAMFIX

Bu sürüm spam/çift mesaj riskini azaltır:

- Aynı `mid` ikinci kez işlenmez.
- Aynı anda işlenen `mid` kilitlenir.
- Aynı kullanıcıdan aynı içerik 30 sn içinde tekrar gelirse atlanır.
- Aynı kullanıcıya aynı cevap 90 sn içinde tekrar gönderilmez.
- Botun kendi echo mesajı müşteriyi susturmaz.
- Sen manuel yazarsan müşteri için bot susturulur.

## Render Environment
Gerekli:
- `ACCESS_TOKEN`
- `VERIFY_TOKEN`
- `OPENAI_API_KEY`

Önerilen:
- Render Settings Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 1 --timeout 120`
- Environment: `WEB_CONCURRENCY=1`
