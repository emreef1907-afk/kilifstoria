import json
import time
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, DUPLICATE_REPLY_WINDOW_SECONDS
from knowledge import PRICE_TEXT, FAQ, HANDOFF_MESSAGE, BUSINESS
from memory import get_user, update_history, duplicate_reply
from detectors import (
    detect_model, detect_design, is_price_question, is_delivery_question, is_cargo_question,
    is_payment_question, is_quality_question, is_model_missing_question, is_design_gallery_question,
    is_location_question, is_trust_question, is_no_more_questions, is_order_intent
)
from guard import sanitize_reply, violates_rules

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = f"""
Sen KilifStoria'nın Instagram DM karşılama asistanısın.

ANA AMAÇ:
Müşteriyi sıcak karşıla, güven ver, telefon modelini öğren, istediği tasarım türünü öğren, sorularını doğru cevapla. Sipariş alma işini işletme sahibine bırak.

KESİN YASAKLAR:
- Adres isteme.
- Telefon numarası isteme.
- Ad-soyad isteme.
- IBAN veya ödeme bilgisi isteme.
- “Siparişinizi alıyorum” deme.
- Sipariş oluşturma.
- Tasarım onayı verme.

İzin verilen bilgi toplama:
- Telefon modeli.
- Tasarım türü: sayfadaki tasarım, kendi fotoğrafı, isimli tasarım, özel tasarım.
- İsimli tasarımda sadece kılıfta yazacak ismi sorabilirsin; müşteri kimlik/ad-soyad bilgisi isteme.

İşletme bilgileri:
- Adana'da hizmet veriyoruz.
- Tüm telefon marka ve modellerine üretim yapılır.
- Sayfadaki telefon modelleri sadece örnek tasarımdır.
- Beğenilen tasarım tüm cihazlara uyarlanır.
- PTT Kargo ile gönderim yapılır.
- 81 ile ücretsiz kargo.
- Sipariş ertesi gün hazırlanır.
- Teslimat ortalama 4 iş günü.
- Ödeme seçenekleri: Havale/EFT, kapıda ödeme, Shopier.
- Shopier: {BUSINESS['shopier']}
- Baskılar UV / Lazer UV baskı teknolojisi ile yapılır; normal kullanımda solma, silinme veya çıkma olmaz.

Fiyat:
Havale/EFT: Tek kılıf 345₺, 2 adet ve üzeri 265₺ / adet.
Kapıda ödeme: Tek kılıf 425₺, 2 adet ve üzeri 345₺ / adet.

KARAR KONTROLÜ:
Cevap vermeden önce sessizce şunu kontrol et:
1. Müşteri bunu gerçekten sordu mu?
2. Fiyat sorulmadıysa fiyat verme.
3. Kargo sorulmadıysa kargo detayına girme.
4. Aynı şeyi tekrar etme.
5. Telefon modeli bilinmiyorsa uygun yerde model sor.
6. Tasarım türü bilinmiyorsa uygun yerde tasarım türü sor.
7. Bilgi tamamlandıysa önce “Aklınıza takılan başka bir soru var mı?” diye sor.
8. Müşterinin sorusu kalmadıysa sadece şu kapanış mesajını ver: {HANDOFF_MESSAGE}

Konuşma tarzı:
- Türkçe konuş.
- Kısa, doğal, samimi ol.
- Tek mesajda 2-3 cümleyi geçme.
- Robot gibi konuşma.
- Aynı cevabı kopyalama.
- Uydurma bilgi verme.

Cevabı SADECE JSON olarak ver:
{{
  "should_reply": true veya false,
  "reply": "müşteriye gönderilecek cevap",
  "handoff": true veya false,
  "facts": {{
    "model": "bilinen telefon modeli veya boş",
    "design": "bilinen tasarım türü veya boş",
    "photo": true veya false,
    "asked_more_questions": true veya false
  }}
}}
"""


def _append_next_question_if_needed(user, reply: str) -> str:
    if user.get("handoff"):
        return reply
    low = reply.lower()
    if not user.get("model") and "telefon model" not in low:
        return reply.rstrip() + "\n\nHangi telefon modeli için düşünüyorsunuz? 😊"
    if user.get("model") and not user.get("design") and "tasarım" not in low:
        return reply.rstrip() + "\n\nNasıl bir tasarım düşünüyorsunuz?"
    return reply


def _direct_answer(user, text: str, has_photo: bool):
    if is_price_question(text):
        return PRICE_TEXT
    if is_delivery_question(text):
        return FAQ["delivery"]
    if is_cargo_question(text):
        return FAQ["cargo"]
    if is_payment_question(text):
        return FAQ["payment"]
    if is_quality_question(text):
        return FAQ["quality"]
    if is_model_missing_question(text):
        return FAQ["model_missing"]
    if is_design_gallery_question(text):
        return FAQ["designs"]
    if is_location_question(text):
        return FAQ["location"]
    if is_trust_question(text):
        return FAQ["trust"]
    if has_photo:
        user["photo"] = True
        user["design"] = user.get("design") or "kendi fotoğrafı"
        if user.get("model"):
            return "Fotoğrafınızı aldım 😊 Bu görsel kılıf tasarımı için kullanılabilir. Aklınıza takılan başka bir soru var mı?"
        return "Fotoğrafınızı aldım 😊 Hangi telefon modeli için hazırlayalım?"
    return None


def _ready_for_handoff(user, text: str) -> bool:
    if not (user.get("model") and user.get("design")):
        return False
    if is_no_more_questions(text):
        return True
    if is_order_intent(text) and user.get("asked_more_questions"):
        return True
    return False


def _update_state_from_text(user, text: str, has_photo: bool):
    model = detect_model(text)
    if model and not user.get("model"):
        user["model"] = model
    design = detect_design(text, has_photo)
    if design and not user.get("design"):
        user["design"] = design
    if has_photo:
        user["photo"] = True


def create_reply(user_id: str, text: str, has_photo: bool = False):
    user = get_user(user_id)
    if user.get("handoff"):
        return None

    _update_state_from_text(user, text, has_photo)

    if _ready_for_handoff(user, text):
        user["handoff"] = True
        return HANDOFF_MESSAGE

    direct = _direct_answer(user, text, has_photo)
    if direct:
        reply = _append_next_question_if_needed(user, direct)
        if user.get("model") and user.get("design") and not user.get("asked_more_questions"):
            user["asked_more_questions"] = True
            reply = reply.rstrip() + "\n\nAklınıza takılan başka bir soru var mı? 😊"
        reply = sanitize_reply(reply)
        if duplicate_reply(user_id, reply, DUPLICATE_REPLY_WINDOW_SECONDS):
            print("Aynı cevap yakın zamanda gönderildi, atlandı.", flush=True)
            return None
        update_history(user_id, "assistant", reply)
        return reply

    # GPT akışı
    update_history(user_id, "user", text + ("\nMüşteri fotoğraf/görsel gönderdi." if has_photo else ""))
    state_info = {
        "telefon_modeli": user.get("model") or "",
        "tasarim_turu": user.get("design") or "",
        "foto_geldi": bool(user.get("photo")),
        "aklina_baska_soru_soruldu": bool(user.get("asked_more_questions")),
        "devredildi": bool(user.get("handoff")),
    }
    conversation = f"Müşteri durumu: {json.dumps(state_info, ensure_ascii=False)}\n\n"
    for msg in user.get("history", [])[-8:]:
        role = "Müşteri" if msg["role"] == "user" else "KilifStoria"
        conversation += f"{role}: {msg['content']}\n"

    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=conversation,
            max_output_tokens=220,
        )
        raw = response.output_text.strip()
        print("GPT RAW:", raw, flush=True)
        parsed = json.loads(raw)
    except Exception as exc:
        print("GPT/JSON HATASI:", str(exc), flush=True)
        parsed = {"should_reply": True, "reply": "Merhaba 😊 Hangi telefon modeli için kılıf düşünüyorsunuz?", "handoff": False, "facts": {}}

    facts = parsed.get("facts", {}) or {}
    if facts.get("model") and not user.get("model"):
        user["model"] = facts["model"]
    if facts.get("design") and not user.get("design"):
        user["design"] = facts["design"]
    if facts.get("photo"):
        user["photo"] = True
    if facts.get("asked_more_questions"):
        user["asked_more_questions"] = True

    if not parsed.get("should_reply", True):
        return None

    reply = (parsed.get("reply") or "").strip()
    handoff = bool(parsed.get("handoff", False))

    # Bilgiler tamam ama henüz başka soru var mı sorulmadıysa önce sor, hemen devretme.
    if user.get("model") and user.get("design") and not user.get("asked_more_questions") and not handoff:
        user["asked_more_questions"] = True
        if "aklınıza takılan" not in reply.lower():
            reply = reply.rstrip() + "\n\nAklınıza takılan başka bir soru var mı? 😊"

    if handoff:
        user["handoff"] = True
        reply = HANDOFF_MESSAGE

    # Guard: yasak bilgi istediyse yeniden yazmak yerine güvenli devret.
    reply = sanitize_reply(reply, fallback=HANDOFF_MESSAGE if user.get("model") and user.get("design") else "Tabii 😊 Size yardımcı olayım. Hangi telefon modeli için düşünüyorsunuz?")

    reply = _append_next_question_if_needed(user, reply)

    if duplicate_reply(user_id, reply, DUPLICATE_REPLY_WINDOW_SECONDS):
        print("Aynı cevap yakın zamanda gönderildi, atlandı.", flush=True)
        return None

    update_history(user_id, "assistant", reply)
    return reply
