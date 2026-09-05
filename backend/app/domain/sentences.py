import re

_SENTENCE_END = re.compile(r"([.!?…]+)([\"\u201d\u2019']*)(\s+|(?=[A-ZÁÉÍÓÚÑÜ])|$)")


def split_ready_sentences(buffer: str) -> tuple[list[str], str]:
    """Pull complete sentences off the front of a streaming buffer."""
    ready: list[str] = []
    while buffer:
        match = _SENTENCE_END.search(buffer)
        nl = buffer.find("\n")
        if nl != -1 and (match is None or nl < match.start()):
            piece = buffer[:nl].strip()
            buffer = buffer[nl + 1 :]
            if piece:
                ready.append(piece)
            continue
        if not match:
            break
        end = match.end()
        piece = buffer[:end].strip()
        buffer = buffer[end:]
        if piece:
            ready.append(piece)
    return ready, buffer


def take_speakable(
    held: str,
    incoming: list[str],
    *,
    min_chars: int = 40,
    max_chars: int = 220,
) -> tuple[list[str], str]:
    """Hold short clauses so Piper is not a burst of four-word clips.

    Callers should pass a low ``min_chars`` (e.g. 1) for the first clip so the
    opening sentence speaks immediately, then raise it (default 40) afterward.
    Questions still flush early regardless of length.
    """
    speakable: list[str] = []
    current = held.strip()
    for piece in incoming:
        piece = piece.strip()
        if not piece:
            continue
        trial = f"{current} {piece}".strip() if current else piece
        if current and len(trial) > max_chars:
            speakable.append(current)
            current = piece
        else:
            current = trial
        if not current:
            continue
        if len(current) >= min_chars or current.endswith("?"):
            speakable.append(current)
            current = ""
    return speakable, current


def split_first_clip(text: str, max_chars: int = 72) -> tuple[str, str]:
    """Keep the opening Piper clip short so first_audio arrives sooner.

    Returns (first_clip, remainder). Prefers a sentence end inside the window,
    else a word boundary near max_chars.
    """
    text = (text or "").strip()
    if not text:
        return "", ""
    if len(text) <= max_chars:
        return text, ""

    window = text[: max_chars + 1]
    best = -1
    for i, ch in enumerate(window):
        if i < 18:
            continue
        if ch in ".!?…":
            best = i + 1
        elif ch in ",;:" and best < 0 and i >= 28:
            best = i + 1
    if best > 0:
        first = text[:best].strip()
        rest = text[best:].strip()
        if first:
            return first, rest

    cut = max_chars
    while cut > 18 and not text[cut - 1].isspace():
        cut -= 1
    if cut <= 18:
        cut = max_chars
    first = text[:cut].strip()
    rest = text[cut:].strip()
    return first, rest
