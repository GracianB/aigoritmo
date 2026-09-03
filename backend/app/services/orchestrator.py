import asyncio
import json
import logging
from collections.abc import AsyncIterator
from contextlib import suppress
from typing import Any

from app.adapters.llm.base import LlmError
from app.adapters.llm.factory import llm_provider_for
from app.adapters.tts.base import TtsError
from app.adapters.tts.factory import tts_provider_for
from app.core.config import Settings
from app.domain.avatars import AvatarCatalog
from app.domain.models import ChatMessage
from app.domain.intent import wants_spread
from app.domain.sentences import split_ready_sentences
from app.domain.speech import prepare_for_speech
from app.services.audio_clips import AudioClipStore
from app.services.conversations import ConversationStore
from app.services.images import ImageStore
from app.adapters.images.pollinations import generate_scene
from app.services.tarot import draw_spread, render_spread
from app.services.vision import analyze_image as analyze_visual

logger = logging.getLogger(__name__)


def sse(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


class Orchestrator:
    def __init__(
        self,
        settings: Settings,
        catalog: AvatarCatalog,
        conversations: ConversationStore,
        clips: AudioClipStore,
        images: ImageStore,
    ) -> None:
        self._settings = settings
        self._catalog = catalog
        self._conversations = conversations
        self._clips = clips
        self._images = images

    async def chat(
        self,
        avatar_id: str,
        user_text: str,
        conversation_id: str | None,
        draw_cards: bool = False,
    ) -> AsyncIterator[str]:
        try:
            avatar = self._catalog.get(avatar_id)
        except KeyError:
            yield sse("error", {"code": "unknown_avatar", "message": f"Avatar desconocido: {avatar_id}"})
            return

        if conversation_id:
            try:
                conv = self._conversations.get(conversation_id)
            except KeyError:
                conv = self._conversations.create(avatar_id)
        else:
            conv = self._conversations.create(avatar_id)

        if conv.avatar_id != avatar_id:
            conv = self._conversations.create(avatar_id)

        self._conversations.append(conv.id, ChatMessage(role="user", content=user_text))
        yield sse("meta", {"conversation_id": conv.id, "avatar_id": avatar.id})

        should_draw = avatar.id in {"arcana", "arcano"} and wants_spread(user_text, explicit=draw_cards)
        if should_draw:
            spread = draw_spread(user_text, avatar.id)
            briefing = "[TIRADA ARCANA]\n" + spread.briefing()
            self._conversations.append(conv.id, ChatMessage(role="system", content=briefing))
            conv = self._conversations.get(conv.id)
            shown = spread.cards[0]
            cards_payload = [
                {"position": c.roman, "name": c.name}
                for c in spread.cards
            ]
            image_id = self._images.save_png(render_spread(spread))
            yield sse(
                "image",
                {
                    "url": f"/media/spreads/{image_id}.png",
                    "caption": f"{shown.roman} {shown.name}",
                    "cards": cards_payload,
                },
            )
            painted = None
            try:
                painted = await asyncio.wait_for(generate_scene(spread), timeout=8.0)
            except Exception:
                logger.warning("pollinations skipped; keeping local card")
            if painted:
                image_id = self._images.save_png(painted)
                yield sse(
                    "image",
                    {
                        "url": f"/media/spreads/{image_id}.png",
                        "caption": f"{shown.roman} {shown.name}",
                        "cards": cards_payload,
                        "replace": True,
                    },
                )


        history = [
            ChatMessage(role="system", content=avatar.system_prompt),
            *conv.messages,
        ]

        llm = llm_provider_for(avatar.llm.provider, self._settings)
        tts = tts_provider_for(avatar.voice.provider, self._settings)
        queue: asyncio.Queue[tuple[str, Any]] = asyncio.Queue()

        async def pump_llm() -> None:
            try:
                async for token in llm.stream(history, avatar.llm.model):
                    await queue.put(("token", token))
                await queue.put(("end", None))
            except LlmError as exc:
                await queue.put(("error", exc))
            except Exception as exc:  # noqa: BLE001 — surface as typed SSE
                await queue.put(("error", LlmError("ollama_unavailable", str(exc))))

        task = asyncio.create_task(pump_llm())
        buffer = ""
        full = ""
        try:
            while True:
                kind, data = await queue.get()
                if kind == "error":
                    logger.warning("llm error: %s", data)
                    yield sse("error", {"code": data.code, "message": data.message})
                    return
                if kind == "end":
                    break
                token = str(data)
                if not full:
                    token = token.lstrip()
                    if token.lower().startswith("assistant"):
                        token = token[9:].lstrip(" :\n")
                if not token:
                    continue
                full += token
                buffer += token
                yield sse("token", {"text": token})
                ready, buffer = split_ready_sentences(buffer)
                for sentence in ready:
                    async for audio_event in self._speak(tts, sentence, avatar.voice):
                        yield audio_event
            leftover = buffer.strip()
            if leftover:
                async for audio_event in self._speak(tts, leftover, avatar.voice):
                    yield audio_event
        finally:
            if not task.done():
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task

        if full.strip():
            self._conversations.append(conv.id, ChatMessage(role="assistant", content=full))
        yield sse("done", {"conversation_id": conv.id})

    async def analyze_image(
        self,
        avatar_id: str,
        image_bytes: bytes,
        prompt: str,
        conversation_id: str | None,
    ) -> dict[str, str]:
        try:
            avatar = self._catalog.get(avatar_id)
        except KeyError as exc:
            raise LlmError("unknown_avatar", f"Avatar desconocido: {avatar_id}") from exc
        if not avatar.capabilities.analyze_image:
            raise LlmError("vision_disabled", f"{avatar.name} no tiene análisis de imagen activado.")

        if conversation_id:
            try:
                conv = self._conversations.get(conversation_id)
            except KeyError:
                conv = self._conversations.create(avatar_id)
        else:
            conv = self._conversations.create(avatar_id)
        if conv.avatar_id != avatar_id:
            conv = self._conversations.create(avatar_id)

        visual_prompt = (
            "El usuario te muestra una imagen. Analízala con cuidado. Describe únicamente lo visible, "
            "separa observación de interpretación y, si contiene cartas de tarot, identifica las cartas "
            "solo cuando tengas confianza suficiente. Después responde a su intención. Pregunta del usuario: "
            + prompt
        )
        text = await analyze_visual(self._settings, avatar, image_bytes, visual_prompt, conv.messages)
        self._conversations.append(conv.id, ChatMessage(role="user", content=f"[IMAGEN MOSTRADA] {prompt}"))
        self._conversations.append(conv.id, ChatMessage(role="assistant", content=text))
        return {"conversation_id": conv.id, "text": text}

    async def speak_text(self, avatar_id: str, text: str) -> str | None:
        try:
            avatar = self._catalog.get(avatar_id)
        except KeyError as exc:
            raise TtsError("unknown_avatar", f"Avatar desconocido: {avatar_id}") from exc
        spoken = prepare_for_speech(text)
        if not spoken:
            return None
        tts = tts_provider_for(avatar.voice.provider, self._settings)
        wav = await tts.synthesize(spoken, avatar.voice.voice_id, options=avatar.voice)
        if not wav:
            return None
        clip_id = self._clips.save(wav)
        return f"/api/audio/{clip_id}"

    async def _speak(self, tts, text: str, voice) -> AsyncIterator[str]:
        spoken = prepare_for_speech(text)
        if not spoken:
            return
        try:
            wav = await tts.synthesize(spoken, voice.voice_id, options=voice)
        except TtsError as exc:
            logger.warning("tts error: %s", exc)
            yield sse("error", {"code": exc.code, "message": exc.message})
            return
        if not wav:
            return
        clip_id = self._clips.save(wav)
        yield sse("audio", {"url": f"/api/audio/{clip_id}", "text": spoken})
