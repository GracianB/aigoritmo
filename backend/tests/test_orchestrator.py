from collections.abc import AsyncIterator

import pytest

from app.adapters.llm.base import LlmError
from app.core.config import get_settings
from app.domain.avatars import AvatarCatalog
from app.domain.models import ChatMessage
from app.services.audio_clips import AudioClipStore
from app.services.conversations import ConversationStore
from app.services.images import ImageStore
from app.services.orchestrator import Orchestrator


class FakeLlm:
    def __init__(self, tokens: list[str]) -> None:
        self.tokens = tokens

    async def stream(self, messages: list[ChatMessage], model: str) -> AsyncIterator[str]:
        for token in self.tokens:
            yield token


class FakeTts:
    async def synthesize(self, text: str, voice_id: str, options=None) -> bytes:
        return f"WAV:{text}".encode("utf-8")


@pytest.fixture
def orchestrator(tmp_path, monkeypatch):
    get_settings.cache_clear()
    settings = get_settings()
    catalog = AvatarCatalog(settings.avatars_dir)
    conv = ConversationStore(tmp_path / "orch.db")
    clips = AudioClipStore(tmp_path / "audio")
    images = ImageStore(tmp_path / "spreads")
    orch = Orchestrator(settings, catalog, conv, clips, images)
    return orch


@pytest.mark.asyncio
async def test_chat_streams_tokens_and_audio(orchestrator, monkeypatch):
    fake_llm = FakeLlm(["Hola. ", "Sigamos."])
    fake_tts = FakeTts()
    monkeypatch.setattr("app.services.orchestrator.llm_provider_for", lambda name, settings: fake_llm)
    monkeypatch.setattr("app.services.orchestrator.tts_provider_for", lambda name, settings: fake_tts)

    events: list[str] = []
    async for chunk in orchestrator.chat("enigma", "¿quién eres?", None):
        events.append(chunk)

    blob = "".join(events)
    assert "event: token" in blob
    assert "event: audio" in blob
    assert "event: done" in blob
    assert "Hola." in blob


@pytest.mark.asyncio
async def test_llm_error_is_typed(orchestrator, monkeypatch):
    class Boom:
        async def stream(self, messages, model):
            raise LlmError("ollama_unavailable", "down")
            yield  # pragma: no cover

    monkeypatch.setattr("app.services.orchestrator.llm_provider_for", lambda name, settings: Boom())
    monkeypatch.setattr("app.services.orchestrator.tts_provider_for", lambda name, settings: FakeTts())

    blob = ""
    async for chunk in orchestrator.chat("enigma", "hola", None):
        blob += chunk
    assert "ollama_unavailable" in blob


@pytest.mark.asyncio
async def test_arcana_emits_spread_image(orchestrator, monkeypatch):
    async def no_scene(_spread):
        return None

    monkeypatch.setattr("app.services.orchestrator.generate_scene", no_scene)
    monkeypatch.setattr("app.services.orchestrator.llm_provider_for", lambda n, s: FakeLlm(["La Torre avisa. "]))
    monkeypatch.setattr("app.services.orchestrator.tts_provider_for", lambda n, s: FakeTts())
    blob = ""
    async for chunk in orchestrator.chat("arcana", "haz una tirada sobre cambio de trabajo", None, True):
        blob += chunk
    assert "event: image" in blob
    assert "/media/spreads/" in blob


@pytest.mark.asyncio
async def test_hola_does_not_emit_spread(orchestrator, monkeypatch):
    monkeypatch.setattr("app.services.orchestrator.llm_provider_for", lambda n, s: FakeLlm(["Hola. "]))
    monkeypatch.setattr("app.services.orchestrator.tts_provider_for", lambda n, s: FakeTts())
    blob = ""
    async for chunk in orchestrator.chat("arcana", "hola", None):
        blob += chunk
    assert "event: image" not in blob
