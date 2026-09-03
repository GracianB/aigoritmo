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

@pytest.mark.asyncio
async def test_tts_receives_cleaned_speech(orchestrator, monkeypatch):
    heard: list[str] = []

    class RecTts:
        async def synthesize(self, text: str, voice_id: str, options=None) -> bytes:
            heard.append(text)
            return f"WAV:{text}".encode("utf-8")

    monkeypatch.setattr("app.services.orchestrator.llm_provider_for", lambda n, s: FakeLlm(["**Hola.** Mira. "]))
    monkeypatch.setattr("app.services.orchestrator.tts_provider_for", lambda n, s: RecTts())
    blob = ""
    async for chunk in orchestrator.chat("enigma", "quién eres", None):
        blob += chunk
    assert heard
    assert all("**" not in item for item in heard)
    assert any("Hola." in item for item in heard)


@pytest.mark.asyncio
async def test_lanza_tirada_emits_image_when_pollinations_hangs(orchestrator, monkeypatch):
    import asyncio

    async def hang(_spread):
        await asyncio.sleep(30)
        return None

    monkeypatch.setattr("app.services.orchestrator.generate_scene", hang)
    monkeypatch.setattr("app.services.orchestrator.llm_provider_for", lambda n, s: FakeLlm(["La carta habla. "]))
    monkeypatch.setattr("app.services.orchestrator.tts_provider_for", lambda n, s: FakeTts())
    blob = ""
    async for chunk in orchestrator.chat("arcana", "lanza una tirada", None):
        blob += chunk
        if "event: image" in blob and "event: token" in blob:
            break
    assert "event: image" in blob
    assert "/media/spreads/" in blob


@pytest.mark.asyncio
async def test_tokens_are_not_blocked_by_slow_pollinations(orchestrator, monkeypatch):
    import asyncio
    import time

    async def hang(_spread):
        await asyncio.sleep(8)
        return None

    monkeypatch.setattr("app.services.orchestrator.generate_scene", hang)
    monkeypatch.setattr("app.services.orchestrator.llm_provider_for", lambda n, s: FakeLlm(["La carta habla. "]))
    monkeypatch.setattr("app.services.orchestrator.tts_provider_for", lambda n, s: FakeTts())
    started = time.monotonic()
    blob = ""
    async for chunk in orchestrator.chat("arcana", "lanza una tirada", None, True):
        blob += chunk
        if "event: token" in blob and "event: image" in blob:
            break
    elapsed = time.monotonic() - started
    assert "event: image" in blob
    assert "event: token" in blob
    assert elapsed < 2.5


@pytest.mark.asyncio
async def test_pollinations_replace_arrives_during_stream(orchestrator, monkeypatch):
    from app.services.tarot import draw_spread, render_spread

    png = render_spread(draw_spread("amor", "arcana"))

    async def paint(_spread):
        return png

    monkeypatch.setattr("app.services.orchestrator.generate_scene", paint)
    monkeypatch.setattr("app.services.orchestrator.llm_provider_for", lambda n, s: FakeLlm(["La Estrella alivia. "]))
    monkeypatch.setattr("app.services.orchestrator.tts_provider_for", lambda n, s: FakeTts())
    blob = ""
    async for chunk in orchestrator.chat("arcana", "haz una tirada sobre el amor", None, True):
        blob += chunk
    assert blob.count("event: image") >= 2
    assert '"replace": true' in blob
