import json
from collections.abc import AsyncIterator

import httpx

from app.adapters.llm.base import LlmError
from app.domain.models import ChatMessage


class OllamaProvider:
    def __init__(self, base_url: str, timeout: float = 180.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = httpx.Timeout(timeout, connect=10.0)

    async def stream(self, messages: list[ChatMessage], model: str) -> AsyncIterator[str]:
        payload = {
            "model": model,
            "stream": True,
            "keep_alive": "30m",
            "options": {"temperature": 0.7, "num_predict": 220, "num_ctx": 1024},
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        url = f"{self._base_url}/api/chat"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code >= 400:
                        body = (await response.aread()).decode("utf-8", errors="replace")
                        raise LlmError(
                            "ollama_unavailable",
                            f"Ollama returned {response.status_code}: {body[:300]}",
                        )
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        data = json.loads(line)
                        if data.get("error"):
                            raise LlmError("ollama_unavailable", str(data["error"]))
                        piece = (data.get("message") or {}).get("content") or ""
                        if piece:
                            yield piece
        except httpx.HTTPError as exc:
            raise LlmError(
                "ollama_unavailable",
                f"Ollama no responde en {self._base_url}. Arranca Ollama y descarga llama3.2:3b.",
            ) from exc
