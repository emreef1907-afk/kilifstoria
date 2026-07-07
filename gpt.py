import json
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL
from knowledge import SYSTEM_PROMPT, HANDOFF_TEXT

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def build_conversation(user: dict, latest_text: str, has_photo: bool) -> str:
    durum = {
        "telefon_modeli_alindi": user.get("model", False),
        "tasarim_istegi_alindi": user.get("design", False),
        "foto_geldi": user.get("photo", False),
        "bot_cevap_sayisi": user.get("bot_replies", 0),
    }

    text = f"Müşteri durumu: {json.dumps(durum, ensure_ascii=False)}\n\n"
    for msg in user.get("history", [])[-8:]:
        role = "Müşteri" if msg["role"] == "user" else "KilifStoria"
        text += f"{role}: {msg['content']}\n"

    text += f"Müşteri son mesajı: {latest_text}\n"
    if has_photo:
        text += "Müşteri fotoğraf/görsel gönderdi. Görseli aldığını kabul ederek cevap ver.\n"

    text += "\nBu müşteriyi Emre'ye devretmenin doğru zamanı mı? Uygunsa handoff true ver."
    return text


def generate_reply(user: dict, latest_text: str, has_photo: bool) -> dict:
    if not client:
        return {"reply": "Merhaba 😊 Hangi telefon modeli için kılıf düşünüyorsunuz?", "handoff": False}

    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=build_conversation(user, latest_text, has_photo),
        max_output_tokens=200,
    )

    raw = response.output_text.strip()
    print("GPT RAW:", raw, flush=True)

    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = {"reply": raw, "handoff": False}

    reply = (parsed.get("reply") or "").strip()
    if not reply:
        reply = "Merhaba 😊 Hangi telefon modeli için kılıf düşünüyorsunuz?"

    return {
        "reply": reply,
        "handoff": bool(parsed.get("handoff", False)),
        "model_detected": bool(parsed.get("model_detected", False)),
        "design_detected": bool(parsed.get("design_detected", False)),
        "photo_acknowledged": bool(parsed.get("photo_acknowledged", False)),
    }
