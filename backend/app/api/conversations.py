from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("/api/conversations/{conversation_id}")
def get_conversation(conversation_id: str, request: Request) -> dict:
    try:
        conv = request.app.state.conversations.get(conversation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return conv.model_dump()


@router.get("/api/avatars/{avatar_id}/conversations")
def list_conversations(avatar_id: str, request: Request) -> dict:
    catalog = request.app.state.catalog
    try:
        catalog.get(avatar_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    items = request.app.state.conversations.list_for_avatar(avatar_id)
    return {
        "conversations": [
            {
                "id": c.id,
                "avatar_id": c.avatar_id,
                "message_count": len(c.messages),
            }
            for c in items
        ]
    }
