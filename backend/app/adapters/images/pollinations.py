"""Free image generation via Pollinations (no API key). Demo-grade, not SLA."""
from urllib.parse import quote

import httpx

from app.services.tarot import Spread


def scene_prompt(spread: Spread) -> str:
    card = spread.cards[0]
    return (
        "a single tarot card in classic tarot-card shape, vertical rectangular naipe "
        "with ornate gold filigree border and rounded corners, "
        f"major arcana {card.name} as the painted scene inside the card, "
        "vintage tarot playing card, one card only, no table, no extra cards, "
        "mystical candlelight, dark background, no letters, no watermark"
    )


async def generate_scene(spread: Spread) -> bytes | None:
    prompt = quote(scene_prompt(spread)[:380])
    url = (
        f"https://image.pollinations.ai/prompt/{prompt}"
        "?width=768&height=1280&nologo=true&model=flux"
    )
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(50.0, connect=8.0), follow_redirects=True) as client:
            response = await client.get(url)
        if response.status_code != 200:
            return None
        kind = (response.headers.get("content-type") or "").lower()
        body = response.content
        if "image" in kind or body[:8] == b"\x89PNG\r\n\x1a\n" or body[:2] == b"\xff\xd8":
            return body
    except httpx.HTTPError:
        return None
    return None
