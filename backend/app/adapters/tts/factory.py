from app.adapters.tts.base import TtsError, TtsProvider
from app.adapters.tts.piper import PiperProvider
from app.core.config import Settings


def tts_provider_for(name: str, settings: Settings) -> TtsProvider:
    key = name.lower().strip()
    if key == "piper":
        return PiperProvider(
            settings.piper_executable,
            settings.piper_models_dir,
            fallback_voice=settings.piper_fallback_voice,
        )
    raise TtsError("unknown_provider", f"Unknown TTS provider: {name}")
