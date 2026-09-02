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