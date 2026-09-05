import re

_SENTENCE_END = re.compile(r"([.!?…]+)([\"»”']*)(\s+|(?=[A-ZÁÉÍÓÚÑ¿¡])|$)")


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
