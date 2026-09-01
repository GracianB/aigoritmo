import re
import unicodedata

_GREETING = re.compile(
    r"^(hola|holi|buenas|buen[oa]s?\s+(d[ií]as|tardes|noches)|hey|hi|hello|que tal|qué tal|ey)[\s!?.]*$",
    re.IGNORECASE,
)
_SPREAD = re.compile(
    r"\b(tirada|tarot|cartas|lanza(?:me)?|tira(?:r|me)?(?:\s+las)?\s+cartas|otra tirada|haz(?:me)? una (?:tirada|lectura))\b",
    re.IGNORECASE,
)
_ACCEPT = re.compile(r"^(s[ií]|ok|vale|adelante|hazlo|dale|lanza|tira)[\s!?.]*$", re.IGNORECASE)


def _fold(text: str) -> str:
    n = unicodedata.normalize("NFD", text.strip())
    return "".join(ch for ch in n if unicodedata.category(ch) != "Mn")


def wants_spread(text: str, *, explicit: bool = False) -> bool:
    """True only if the user asked for a reading, not a greeting or small talk."""
    if explicit:
        return True
    raw = text.strip()
    if not raw or _GREETING.match(_fold(raw)):
        return False
    if _ACCEPT.match(raw) or _ACCEPT.match(_fold(raw)):
        return True
    return bool(_SPREAD.search(raw))
