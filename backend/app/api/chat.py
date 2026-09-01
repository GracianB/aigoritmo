from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    avatar_id: str = "arcana"
    conversation_id: str | None = None
    draw_cards: bool = False


@router.post("/api/chat")
async def chat(body: ChatRequest, request: Request) -> StreamingResponse:
    orchestrator = request.app.state.orchestrator

    async def events():
        async for chunk in orchestrator.chat(body.avatar_id, body.message.strip(), body.conversation_id, body.draw_cards):
            yield chunk

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
