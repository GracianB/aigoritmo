from typing import Protocol

from app.domain.models import VoiceConfig


class TtsError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class TtsProvider(Protocol):
    async def synthesize(self, text: str, voice_id: str, options: VoiceConfig | None = None) -> bytes:
        ...
