from __future__ import annotations

from dataclasses import dataclass

from app.adapters.llm.base import LlmError, LlmProvider
from app.adapters.llm.ollama import OllamaProvider
from app.adapters.llm.openai import OpenAIProvider
from app.adapters.llm.spacexai import SpaceXAIProvider
from app.core.config import Settings
from app.domain.models import Avatar


@dataclass(frozen=True)
class ResolvedLlm:
    """Chosen chat/vision provider + model name after resolution."""

    provider: str
    model: str
    source: str  # "force" | "preferred" | "fallback"


def provider_configured(name: str, settings: Settings) -> bool:
    """True when the provider can be used without missing credentials.

    Ollama is always "configured" here (reachability is a separate health check).
    SpaceXAI / xAI requires a non-empty XAI_API_KEY.
    OpenAI requires a non-empty OPENAI_API_KEY.
    """
    key = (name or "").lower().strip()
    if key == "ollama":
        return True
    if key == "spacexai":
        return bool((settings.xai_api_key or "").strip())
    if key == "openai":
        return bool((settings.openai_api_key or "").strip())
    return False


def llm_provider_for(name: str, settings: Settings) -> LlmProvider:
    key = name.lower().strip()
    if key == "ollama":
        return OllamaProvider(settings.ollama_base_url, timeout=settings.ollama_timeout)
    if key == "spacexai":
        return SpaceXAIProvider(settings.xai_api_key, settings.xai_base_url)
    if key == "openai":
        return OpenAIProvider(settings.openai_api_key, settings.openai_base_url)
    raise LlmError("unknown_provider", f"Unknown LLM provider: {name}")


def _global_override(settings: Settings) -> str:
    """LLM_PROVIDER / FORCE_LLM_PROVIDER when set (non-empty)."""
    force = (settings.force_llm_provider or "").strip()
    if force:
        return force.lower()
    override = (settings.llm_provider or "").strip()
    if override:
        return override.lower()
    return ""


def _model_for_provider(
    provider: str,
    avatar: Avatar,
    settings: Settings,
    *,
    use_catalog: bool,
) -> str:
    if provider == "spacexai":
        if use_catalog and (avatar.llm.catalog_model or "").strip():
            return avatar.llm.catalog_model.strip()
        return (settings.xai_model or "grok-4.5").strip()
    if provider == "openai":
        if use_catalog and (avatar.llm.catalog_model or "").strip():
            return avatar.llm.catalog_model.strip()
        return (settings.openai_model or "gpt-4.1").strip()
    # ollama (and any other local-style provider)
    if use_catalog and (avatar.llm.catalog_model or "").strip():
        return avatar.llm.catalog_model.strip()
    return (avatar.llm.model or settings.ollama_model).strip()


def resolve_chat_llm(avatar: Avatar, settings: Settings) -> ResolvedLlm:
    """Resolve chat LLM provider + model.

    Order (documented for API day / README):
      1. Global override — Settings.force_llm_provider (FORCE_LLM_PROVIDER)
         or Settings.llm_provider (LLM_PROVIDER) when non-empty.
         Values: openai | spacexai | ollama.
      2. avatar.llm.preferred_provider if set AND that provider is configured
         (API key present when required) → preferred + catalog_model
         (or Settings.xai_model / openai_model when catalog_model is empty).
      3. Fallback — avatar.llm.provider + avatar.llm.model (typically ollama).
    """
    override = _global_override(settings)
    if override:
        return ResolvedLlm(
            provider=override,
            model=_model_for_provider(override, avatar, settings, use_catalog=False),
            source="force",
        )

    preferred = (avatar.llm.preferred_provider or "").strip().lower()
    if preferred and provider_configured(preferred, settings):
        return ResolvedLlm(
            provider=preferred,
            model=_model_for_provider(preferred, avatar, settings, use_catalog=True),
            source="preferred",
        )

    fallback = (avatar.llm.provider or "ollama").strip().lower()
    return ResolvedLlm(
        provider=fallback,
        model=(avatar.llm.model or settings.ollama_model).strip(),
        source="fallback",
    )


def resolve_vision_llm(avatar: Avatar, settings: Settings) -> ResolvedLlm:
    """Same provider resolution as chat; vision-specific model from Settings."""
    chat = resolve_chat_llm(avatar, settings)
    if chat.provider == "spacexai":
        model = (settings.xai_vision_model or settings.xai_model or "grok-4.5").strip()
    elif chat.provider == "openai":
        model = (settings.openai_vision_model or settings.openai_model or "gpt-4.1").strip()
    else:
        model = (settings.ollama_vision_model or settings.ollama_model).strip()
    return ResolvedLlm(provider=chat.provider, model=model, source=chat.source)
