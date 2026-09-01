import re

_SENTENCE_END = re.compile(r"([.!?…]+)([\"»”']*)(\s+|$)")


def split_ready_sentences(buffer: str) -> tuple[list[str], str]:
    """Pull complete sentences off the front of a streaming buffer."""
    ready: list[str] = []
    while buffer:
        match = _SENTENCE_END.search(buffer)
        if not match:
            break
        if match.lastindex and match.group(3) == "" and match.end() == len(buffer):
            # Trailing terminator with no following whitespace yet — still a sentence.
            pass
        end = match.end()
        piece = buffer[:end].strip()
        buffer = buffer[end:]
        if piece:
            ready.append(piece)
    return ready, buffer
