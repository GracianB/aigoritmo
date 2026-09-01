from collections.abc import AsyncIterator
from typing import Protocol

from app.domain.models import ChatMessage


class LlmError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class LlmProvider(Protocol):
    async def stream(self, messages: list[ChatMessage], model: str) -> AsyncIterator[str]:
        ...
