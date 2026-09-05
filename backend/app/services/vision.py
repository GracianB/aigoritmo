from __future__ import annotations

import base64
from io import BytesIO

import httpx
from PIL import Image, UnidentifiedImageError

from app.adapters.llm.base import LlmError
from app.adapters.llm.factory import resolve_vision_llm
from app.core.config import Settings
from app.domain.models import Avatar, ChatMessage

MAX_IMAGE_BYTES = 12 * 1024 * 1024
MAX_EDGE = 1600


def normalize_image(raw: bytes) -> tuple[bytes, str]:
    if not raw:
        raise LlmError("invalid_image", "La imagen está vacía.")
    if len(raw) > MAX_IMAGE_BYTES:
        raise LlmError("image_too_large", "La imagen supera el límite de 12 MB.")
    try:
        image = Image.open(BytesIO(raw))
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise LlmError("invalid_image", "El archivo no es una imagen válida.") from exc

    image = image.convert("RGB")
    image.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=88, optimize=True)
    return buffer.getvalue(), "image/jpeg"


async def analyze_image(
    settings: Settings,
    avatar: Avatar,
    image_bytes: bytes,
    prompt: str,
    history: list[ChatMessage],
) -> str:
    normalized, mime = normalize_image(image_bytes)
    resolved = resolve_vision_llm(avatar, settings)
    provider = resolved.provider
    if provider == "ollama":
        return await _ollama(settings, avatar, normalized, prompt, history, model=resolved.model)
    if provider == "spacexai":
        return await _xai(settings, avatar, normalized, mime, prompt, history, model=resolved.model)
    raise LlmError("vision_unsupported", f"El proveedor {provider} no soporta vision en esta app.")


async def _ollama(
    settings: Settings,
    avatar: Avatar,
    image_bytes: bytes,
    prompt: str,
    history: list[ChatMessage],
    model: str | None = None,
) -> str:
    messages = [{"role": "system", "content": avatar.system_prompt}]
    for message in history[-10:]:
        messages.append({"role": message.role, "content": message.content})
    messages.append(
        {
            "role": "user",
            "content": prompt,
            "images": [base64.b64encode(image_bytes).decode("ascii")],
        }
    )
    payload = {
        "model": model or settings.ollama_vision_model,
        "stream": False,
        "messages": messages,
        "options": {"temperature": 0.45},
    }
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(f"{settings.ollama_base_url.rstrip('/')}/api/chat", json=payload)
            if response.status_code >= 400:
                raise LlmError(
                    "ollama_vision_unavailable",
                    f"Ollama Vision respondió {response.status_code}: {response.text[:300]}",
                )
            data = response.json()
            text = ((data.get("message") or {}).get("content") or "").strip()
            if not text:
                raise LlmError("vision_empty", "El modelo visual no devolvió una interpretación.")
            return text
    except httpx.HTTPError as exc:
        raise LlmError(
            "ollama_vision_unavailable",
            f"No se pudo usar visión local. Instala el modelo: ollama pull {settings.ollama_vision_model}",
        ) from exc


async def _xai(
    settings: Settings,
    avatar: Avatar,
    image_bytes: bytes,
    mime: str,
    prompt: str,
    history: list[ChatMessage],
    model: str | None = None,
) -> str:
    if not settings.xai_api_key:
        raise LlmError("spacexai_unconfigured", "Falta XAI_API_KEY para analizar imágenes con xAI.")

    messages: list[dict] = [{"role": "system", "content": avatar.system_prompt}]
    for message in history[-10:]:
        if message.role != "system":
            messages.append({"role": message.role, "content": message.content})
    data_url = f"data:{mime};base64,{base64.b64encode(image_bytes).decode('ascii')}"
    messages.append(
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }
    )
    payload = {"model": model or settings.xai_vision_model, "messages": messages, "stream": False}
    headers = {"Authorization": f"Bearer {settings.xai_api_key}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{settings.xai_base_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            )
            if response.status_code >= 400:
                raise LlmError("spacexai_vision_unavailable", f"xAI respondió {response.status_code}: {response.text[:300]}")
            data = response.json()
            text = (((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
            if not text:
                raise LlmError("vision_empty", "El modelo visual no devolvió una interpretación.")
            return text
    except httpx.HTTPError as exc:
        raise LlmError("spacexai_vision_unavailable", "No se pudo contactar con xAI para analizar la imagen.") from exc
