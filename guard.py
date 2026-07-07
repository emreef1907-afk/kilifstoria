import re
from knowledge import HANDOFF_MESSAGE

FORBIDDEN_PATTERNS = [
    r"adres\w*\s+(al|iste|paylaş|yaz|gönder)",
    r"telefon\s+numara\w*",
    r"numara\w*\s+(al|iste|paylaş|yaz|gönder)",
    r"ad[ -]?soyad",
    r"iban",
    r"siparişinizi\s+al",
    r"sipariş\s+için\s+isim",
    r"isim,\s*adres",
    r"adres\s+ve\s+telefon",
]


def violates_rules(reply: str) -> bool:
    text = (reply or "").lower()
    return any(re.search(pattern, text) for pattern in FORBIDDEN_PATTERNS)


def sanitize_reply(reply: str, fallback: str = None) -> str:
    if not reply:
        return fallback or "Merhaba 😊 Hangi telefon modeli için kılıf düşünüyorsunuz?"
    if violates_rules(reply):
        return fallback or HANDOFF_MESSAGE
    return reply.strip()
