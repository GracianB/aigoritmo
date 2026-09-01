from fastapi import APIRouter, Request
import httpx

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
    return {
        "status": "ok",
        "llm_provider": settings.llm_provider,
        "chat_model": settings.ollama_model,
        "avatar_count": len(catalog.list()),
        "avatars": [avatar.id for avatar in catalog.list()],
        "default_avatar": settings.default_avatar,
        "piper_executable": settings.piper_executable.is_file(),
        "piper_models_dir": settings.piper_models_dir.is_dir(),
        "piper_voices": voices,
        "ollama": ollama_ok,
        "ollama_models": models,
        "ollama_chat_ready": settings.ollama_model in models or f"{settings.ollama_model}:latest" in models,
    }
