from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from app.adapters.tts.base import TtsError

router = APIRouter()


class SpeakRequest(BaseModel):
    avatar_id: str = "arcana"
    text: str = Field(min_length=1, max_length=4000)


@router.post("/api/speak")
async def speak(body: SpeakRequest, request: Request) -> JSONResponse:
    try:
        url = await request.app.state.orchestrator.speak_text(body.avatar_id, body.text)
    except TtsError as exc:
        return JSONResponse(status_code=422, content={"code": exc.code, "message": exc.message})
    if not url:
        return JSONResponse(status_code=422, content={"code": "empty_speech", "message": "Nada que decir."})
    return JSONResponse({"url": url})


@router.get("/api/audio/{clip_id}")
def get_audio(clip_id: str, request: Request) -> FileResponse:
    if "/" in clip_id or "\\" in clip_id or ".." in clip_id:
        raise HTTPException(status_code=400, detail="invalid clip id")
    try:
        path = request.app.state.clips.path_for(clip_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="audio not found") from exc
    return FileResponse(path, media_type="audio/wav")
