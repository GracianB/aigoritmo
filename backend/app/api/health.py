from fastapi import APIRouter, Request
import httpx

from app.adapters.llm.factory import provider_configured

router = APIRouter()

DEMO_VOICES = ("es_AR-daniela-high", "es_MX-gevy-high", "es_MX-laura-high", "es_ES-davefx-medium")


@router.get("/health")
def health(request: Request) -> dict:
    settings = request.app.state.settings
    catalog = request.app.state.catalog
    ollama_ok = False
    models: list[str] = []
    try:
        response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=2.5)
        ollama_ok = response.status_code == 200
        if ollama_ok:
            models = [item.get("name", "") for item in response.json().get("models", [])]
    except httpx.HTTPError:
        ollama_ok = False
    voices = {
        voice: (settings.piper_models_dir / f"{voice}.onnx").is_file()
        for voice in DEMO_VOICES
    }
    xai_ready = provider_configured("spacexai", settings)
    override = (settings.force_llm_provider or settings.llm_provider or "").strip() or None
    return {
        "status": "ok",
        "llm_provider_override": override,
        "providers": {
            "ollama": {
                "ready": ollama_ok,
                "configured": True,
                "base_url": settings.ollama_base_url,
                "chat_model": settings.ollama_model,
                "vision_model": settings.ollama_vision_model,
                "models": models,
                "chat_ready": settings.ollama_model in models
                or f"{settings.ollama_model}:latest" in models,
            },
            "spacexai": {
                "ready": xai_ready,
                "configured": xai_ready,
                "base_url": settings.xai_base_url,
                "chat_model": settings.xai_model,
                "vision_model": settings.xai_vision_model,
                # Never expose XAI_API_KEY — only presence.
                "api_key_present": xai_ready,
            },
        },
        # Backward-compatible flat fields (ollama-centric demo).
        "llm_provider": override or "auto",
        "chat_model": settings.ollama_model,
        "avatar_count": len(catalog.list()),
        "avatars": [avatar.id for avatar in catalog.list()],
        "default_avatar": settings.default_avatar,
        "piper_executable": settings.piper_executable.is_file(),
        "piper_models_dir": settings.piper_models_dir.is_dir(),
        "piper_voices": voices,
        "ollama": ollama_ok,
        "ollama_models": models,
        "ollama_chat_ready": settings.ollama_model in models
        or f"{settings.ollama_model}:latest" in models,
        "spacexai_ready": xai_ready,
    }
