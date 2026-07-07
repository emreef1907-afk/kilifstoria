PHONE_WORDS = [
    "iphone", "samsung", "xiaomi", "redmi", "oppo", "tecno", "realme",
    "huawei", "honor", "vivo", "reeder", "infinix", "poco", "galaxy",
    "note", "pro", "max", "plus", "a13", "a14", "a15", "a16", "a23", "a24",
    "a34", "a35", "a54", "a55", "s23", "s24", "s25"
]

DESIGN_WORDS = [
    "foto", "fotoğraf", "fotograf", "resim", "kendi", "isim", "isimli",
    "özel", "ozel", "sayfadaki", "tasarım", "tasarim", "model", "bunu",
    "şunu", "sunu", "aynısı", "aynisi"
]


def detect_model(text: str) -> bool:
    t = (text or "").lower().strip()
    if len(t) < 2:
        return False
    if any(word in t for word in PHONE_WORDS):
        return True
    # iPhone 13 gibi sadece sayı yazılırsa riskli; tek başına 13 model sayılmasın.
    return False


def detect_design(text: str, has_photo: bool = False) -> bool:
    if has_photo:
        return True
    t = (text or "").lower().strip()
    return any(word in t for word in DESIGN_WORDS)
