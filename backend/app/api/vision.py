from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse

from app.adapters.llm.base import LlmError

router = APIRouter()


@router.post("/api/vision/analyze")
async def analyze(
    request: Request,
    image: UploadFile = File(...),
    avatar_id: str = Form("arcana"),
    conversation_id: str | None = Form(None),
    prompt: str = Form("Interpreta lo que ves en esta imagen y relaciónalo con nuestra conversación."),
) -> JSONResponse:
    data = await image.read()
    try:
        result = await request.app.state.orchestrator.analyze_image(
            avatar_id=avatar_id,
            image_bytes=data,
            prompt=prompt.strip() or "Interpreta esta imagen.",
            conversation_id=conversation_id,
        )
    except LlmError as exc:
        return JSONResponse(status_code=422, content={"code": exc.code, "message": exc.message})
    return JSONResponse(result)
