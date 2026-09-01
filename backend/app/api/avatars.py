from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("/api/avatars")
def list_avatars(request: Request) -> dict:
    catalog = request.app.state.catalog
    return {"avatars": [a.model_dump() for a in catalog.list()]}


@router.get("/api/avatars/{avatar_id}")
def get_avatar(avatar_id: str, request: Request) -> dict:
    catalog = request.app.state.catalog
    try:
        return catalog.get(avatar_id).model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
