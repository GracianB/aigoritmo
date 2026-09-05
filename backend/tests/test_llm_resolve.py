"""LLM provider resolution: override → preferred (if keyed) → avatar fallback."""

from app.adapters.llm.factory import (
    provider_configured,
    resolve_chat_llm,
    resolve_vision_llm,
)
from app.core.config import Settings
from app.domain.models import Avatar, Capabilities, LlmConfig, VoiceConfig


def _avatar(
    *,
    provider: str = "ollama",
    model: str = "llama3.2:3b",
    preferred_provider: str | None = "spacexai",
    catalog_model: str | None = "grok-4.5",
) -> Avatar:
    return Avatar(
        id="arcana",
        name="Arcana",
        poster="/media/image/arcana.jpg",
        voice=VoiceConfig(voice_id="es_AR-daniela-high"),
        llm=LlmConfig(
            provider=provider,  # type: ignore[arg-type]
            model=model,
            preferred_provider=preferred_provider,  # type: ignore[arg-type]
            catalog_model=catalog_model,
        ),
        system_prompt="test",
        capabilities=Capabilities(),
    )


def test_fallback_without_key_uses_ollama():
    settings = Settings(xai_api_key="", llm_provider="", force_llm_provider="")
    avatar = _avatar()
    resolved = resolve_chat_llm(avatar, settings)
    assert resolved.provider == "ollama"
    assert resolved.model == "llama3.2:3b"
    assert resolved.source == "fallback"
    assert not provider_configured("spacexai", settings)


def test_preferred_with_key_uses_spacexai_and_catalog_model():
    settings = Settings(xai_api_key="test-key-not-real", llm_provider="", force_llm_provider="")
    avatar = _avatar(catalog_model="grok-4.5")
    resolved = resolve_chat_llm(avatar, settings)
    assert resolved.provider == "spacexai"
    assert resolved.model == "grok-4.5"
    assert resolved.source == "preferred"
    assert provider_configured("spacexai", settings)


def test_preferred_without_catalog_uses_settings_xai_model():
    settings = Settings(
        xai_api_key="test-key-not-real",
        xai_model="grok-4.5",
        llm_provider="",
        force_llm_provider="",
    )
    avatar = _avatar(catalog_model=None)
    resolved = resolve_chat_llm(avatar, settings)
    assert resolved.provider == "spacexai"
    assert resolved.model == "grok-4.5"
    assert resolved.source == "preferred"


def test_force_llm_provider_wins_even_without_preferred_key():
    settings = Settings(
        xai_api_key="",
        force_llm_provider="ollama",
        llm_provider="",
    )
    avatar = _avatar(preferred_provider="spacexai")
    resolved = resolve_chat_llm(avatar, settings)
    assert resolved.provider == "ollama"
    assert resolved.source == "force"


def test_llm_provider_env_override_to_spacexai():
    settings = Settings(
        xai_api_key="test-key-not-real",
        llm_provider="spacexai",
        force_llm_provider="",
        xai_model="grok-4.5",
    )
    avatar = _avatar(preferred_provider=None, catalog_model=None)
    resolved = resolve_chat_llm(avatar, settings)
    assert resolved.provider == "spacexai"
    assert resolved.model == "grok-4.5"
    assert resolved.source == "force"


def test_force_beats_llm_provider():
    settings = Settings(
        xai_api_key="test-key-not-real",
        force_llm_provider="ollama",
        llm_provider="spacexai",
    )
    avatar = _avatar()
    resolved = resolve_chat_llm(avatar, settings)
    assert resolved.provider == "ollama"
    assert resolved.source == "force"


def test_vision_follows_chat_provider_with_vision_model():
    settings = Settings(
        xai_api_key="test-key-not-real",
        xai_vision_model="grok-4.5",
        llm_provider="",
        force_llm_provider="",
    )
    avatar = _avatar()
    resolved = resolve_vision_llm(avatar, settings)
    assert resolved.provider == "spacexai"
    assert resolved.model == "grok-4.5"
    assert resolved.source == "preferred"
