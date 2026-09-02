import re

_MD_BOLD = re.compile(r"\*\*(.+?)\*\*")
_MD_ITAL = re.compile(r"(?<!\*)\*(.+?)\*(?!\*)")
_MD_CODE = re.compile(r"`([^`]+)`")
_MD_HEAD = re.compile(r"^#{1,6}\s*", re.MULTILINE)
_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_URL = re.compile(r"https?://\S+")
_BULLET = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+", re.MULTILINE)
_EMOJI = re.compile(
    "["
    "\U0001f300-\U0001faff"
    "\U00002700-\U000027bf"
    "\U0001f1e6-\U0001f1ff"
    "]+"
)
_MULTI_SPACE = re.compile(r"\s+")
_BRACKETS = re.compile(r"[\[\]{}]")


def prepare_for_speech(text: str) -> str:
    """Strip markup so Piper speaks natural Spanish, not asterisks and URLs."""
    if not text or not text.strip():
        return ""
    out = text.replace("\r\n", "\n")
    out = _URL.sub(" ", out)
    out = _MD_LINK.sub(r"\1", out)
    out = _MD_CODE.sub(r"\1", out)
    out = _MD_BOLD.sub(r"\1", out)
    out = _MD_ITAL.sub(r"\1", out)
    out = _MD_HEAD.sub("", out)
    out = _BULLET.sub("", out)
    out = out.replace("**", "").replace("__", "")
    out = out.replace("—", ", ").replace("–", ", ").replace("…", ". ")
    out = _EMOJI.sub(" ", out)
    out = _BRACKETS.sub(" ", out)
    out = _MULTI_SPACE.sub(" ", out).strip(" \t\n\r-–—*")
    if sum(ch.isalpha() for ch in out) < 2:
        return ""
    return out