import json
import time
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, FINAL_HANDOFF_MESSAGE, MIN_SECONDS_BETWEEN_REPLIES, MAX_BOT_REPLIES
from knowledge import SYSTEM_PROMPT
from memory import get_user, add_history, register_bot_reply, mark_handoff
from detectors import has_phone_model, has_design, direct_answer, no_more_questions

client = OpenAI(api_key=OPENAI_API_KEY)


def update_state(user: dict, text: str, has_photo: bool) -> None:
    if has_photo:
        user["photo"] = True
        user["design"] = True
    if has_phone_model(text):
        user["model"] = True
    if has_design(text):
        user["design"] = True


def maybe_state_followup(user: dict, base_reply: str) -> str:
    """Bilinen cevaplardan sonra konuşmayı hedefe döndürür."""
    if not user.get("model"):
        return base_reply + "\n\nBu arada hangi telefon modeli için düşünüyorsunuz? 😊"
    if not user.get("design"):
        return base_reply + "\n\nNasıl bir tasarım düşünüyorsunuz? Sayfamızdaki tasarımlardan biri, kendi fotoğrafınız, isimli veya özel tasarım olabilir."
    if not user.get("asked_more_questions"):
        user["asked_more_questions"] = True
        return base_reply + "\n\nAklınıza takılan başka bir soru var mı? 😊"
    return base_reply


def build_conversation(user: dict, new_text: str, has_photo: bool) -> str:
    status = {
        "telefon_modeli_alindi": user.get("model", False),
        "tasarim_istegi_alindi": user.get("design", False),
        "foto_geldi": user.get("photo", False),
        "daha_once_baska_soru_soruldu_mu": user.get("asked_more_questions", False),
        "bot_cevap_sayisi": user.get("bot_replies", 0),
    }
    lines = [f"Müşteri durumu: {json.dumps(status, ensure_ascii=False)}", ""]
    for msg in user.get("history", [])[-8:]:
        role = "Müşteri" if msg["role"] == "user" else "KilifStoria"
        lines.append(f"{role}: {msg['content']}")
    lines.append(f"Müşteri: {new_text}")
    if has_photo:
        lines.append("Not: Müşteri fotoğraf/görsel gönderdi. Bunu gönderilmiş kabul et.")
    return "\n".join(lines)


def generate_reply(user_id: str, text: str, has_photo: bool = False) -> str | None:
    user = get_user(user_id)

    if user.get("handoff"):
        return None

    if user.get("bot_replies", 0) >= MAX_BOT_REPLIES:
        mark_handoff(user_id)
        return None

    now = time.time()
    if now - user.get("last_reply_time", 0) < MIN_SECONDS_BETWEEN_REPLIES:
        print("Kısa sürede tekrar event geldi, cevap atlanıyor.", flush=True)
        return None

    # Manuel devretme öncesi: müşteri sorum kalmadı derse bitir.
    if user.get("asked_more_questions") and no_more_questions(text):
        mark_handoff(user_id)
        register_bot_reply(user_id)
        return FINAL_HANDOFF_MESSAGE

    update_state(user, text, has_photo)

    # Görsel geldiyse tekrar foto isteme; direkt doğru bağlamı ver.
    if has_photo:
        base = "Fotoğrafınızı aldım 😊 Tasarım ekibimiz bu görsele uygun çalışma hazırlayabilir."
        if not user.get("model"):
            reply = base + "\n\nHangi telefon modeli için olacak?"
        else:
            user["asked_more_questions"] = True
            reply = base + "\n\nAklınıza takılan başka bir soru var mı? 😊"
        add_history(user_id, "user", "Müşteri fotoğraf gönderdi.")
        add_history(user_id, "assistant", reply)
        register_bot_reply(user_id)
        return reply

    direct = direct_answer(text)
    if direct:
        reply = maybe_state_followup(user, direct)
        add_history(user_id, "user", text)
        add_history(user_id, "assistant", reply)
        register_bot_reply(user_id)
        return reply

    conversation = build_conversation(user, text, has_photo)

    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=conversation,
        max_output_tokens=220,
    )
    raw = response.output_text.strip()
    print("GPT RAW:", raw, flush=True)

    try:
        parsed = json.loads(raw)
        reply = (parsed.get("reply") or "").strip()
        handoff = bool(parsed.get("handoff", False))
        facts = parsed.get("facts") or {}
        if facts.get("model"):
            user["model"] = True
        if facts.get("design"):
            user["design"] = True
        if facts.get("photo"):
            user["photo"] = True
        if facts.get("asked_if_more_questions"):
            user["asked_more_questions"] = True
    except Exception:
        reply = raw
        handoff = False

    if not reply:
        reply = "Merhaba 😊 Hangi telefon modeli için kılıf düşünüyorsunuz?"

    # Gereken iki bilgi tamamlandıysa, hemen kapatma; önce başka soru var mı diye sor.
    if user.get("model") and user.get("design") and not user.get("asked_more_questions"):
        user["asked_more_questions"] = True
        reply = "Çok güzel 😊 Aklınıza takılan başka bir soru var mı?"
        handoff = False

    if handoff:
        reply = FINAL_HANDOFF_MESSAGE
        mark_handoff(user_id)

    add_history(user_id, "user", text)
    add_history(user_id, "assistant", reply)
    register_bot_reply(user_id)
    return reply
