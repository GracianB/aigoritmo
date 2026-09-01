from app.adapters.llm.base import LlmError, LlmProvider
from app.adapters.llm.ollama import OllamaProvider
from app.adapters.llm.spacexai import SpaceXAIProvider
from app.core.config import Settings


def llm_provider_for(name: str, settings: Settings) -> LlmProvider:
    key = name.lower().strip()
    if key == "ollama":
        return OllamaProvider(settings.ollama_base_url, timeout=settings.ollama_timeout)
    if key == "spacexai":
        return SpaceXAIProvider(settings.xai_api_key, settings.xai_base_url)
    raise LlmError("unknown_provider", f"Unknown LLM provider: {name}")
