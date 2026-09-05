import json
from collections.abc import AsyncIterator

import httpx

from app.adapters.llm.base import LlmError
from app.domain.models import ChatMessage


class OpenAIProvider:
    """OpenAI Chat Completions streaming (same SSE shape as SpaceXAI)."""

    def __init__(self, api_key: str, base_url: str, timeout: float = 120.0) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def stream(self, messages: list[ChatMessage], model: str) -> AsyncIterator[str]:
        if not self._api_key:
            raise LlmError(
                "openai_unconfigured",
                "Falta OPENAI_API_KEY. Usa LLM_PROVIDER=ollama para la demo local.",
            )
        payload = {
            "model": model,
            "stream": True,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self._base_url}/chat/completions"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                async with client.stream("POST", url, json=payload, headers=headers) as response:
                    if response.status_code >= 400:
                        body = (await response.aread()).decode("utf-8", errors="replace")
                        raise LlmError(
                            "openai_unavailable",
                            f"OpenAI returned {response.status_code}: {body[:300]}",
                        )
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            break
                        chunk = json.loads(data)
                        delta = (chunk.get("choices") or [{}])[0].get("delta") or {}
                        piece = delta.get("content") or ""
                        if piece:
                            yield piece
        except httpx.HTTPError as exc:
            raise LlmError("openai_unavailable", "No se pudo contactar con OpenAI.") from exc