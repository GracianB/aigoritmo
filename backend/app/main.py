import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.audio import router as audio_router
from app.api.avatars import router as avatars_router
from app.api.chat import router as chat_router
from app.api.conversations import router as conversations_router
from app.api.health import router as health_router
from app.api.vision import router as vision_router
from app.core.config import get_settings
from app.domain.avatars import AvatarCatalog
from app.services.audio_clips import AudioClipStore
from app.services.conversations import ConversationStore
from app.services.images import ImageStore
from app.services.orchestrator import Orchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

LOCAL_ORIGINS = (
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    catalog = AvatarCatalog(settings.avatars_dir)
    conversations = ConversationStore(settings.database_path)
    clips = AudioClipStore(settings.media_dir / "audio")
    images = ImageStore(settings.media_dir / "spreads")
    app.state.settings = settings
    app.state.catalog = catalog
    app.state.conversations = conversations
    app.state.clips = clips
    app.state.images = images
    app.state.orchestrator = Orchestrator(settings, catalog, conversations, clips, images)
    logger.info("avatars loaded: %s", [a.id for a in catalog.list()])
    logger.info("piper: %s models=%s", settings.piper_executable, settings.piper_models_dir)

    async def warmup_ollama() -> None:
        import httpx

        url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=5.0)) as client:
                await client.post(
                    url,
                    json={
                        "model": settings.ollama_model,
                        "prompt": "ok",
                        "stream": False,
                        "keep_alive": "60m",
                        "options": {"num_predict": 1},
                    },
                )
            logger.info("ollama warmup done: %s", settings.ollama_model)
        except Exception as exc:  # noqa: BLE001
            logger.warning("ollama warmup failed: %s", exc)

    async def warmup_piper() -> None:
        for avatar_id in ("arcana", "arcano"):
            try:
                avatar = catalog.get(avatar_id)
                url = await app.state.orchestrator.speak_text(avatar.id, avatar.welcome)
                logger.info("piper warmup done: %s %s -> %s", avatar.id, avatar.voice.voice_id, url)
            except Exception as exc:  # noqa: BLE001
                logger.warning("piper warmup failed (%s): %s", avatar_id, exc)

    import asyncio

    asyncio.create_task(warmup_ollama())
    asyncio.create_task(warmup_piper())
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Aigoritmo", version="2.0.0-demo", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(LOCAL_ORIGINS),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(avatars_router)
    app.include_router(chat_router)
    app.include_router(conversations_router)
    app.include_router(audio_router)
    app.include_router(vision_router)
    if settings.media_dir.is_dir():
        app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")
    return app


app = create_app()
