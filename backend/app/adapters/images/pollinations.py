"""Free image generation via Pollinations (no API key). Demo-grade, not SLA."""
from urllib.parse import quote

import httpx

from app.services.tarot import Spread


def scene_prompt(spread: Spread) -> str:
    cards = ", ".join(f"{c.position}: {c.name}" for c in spread.cards)
    return (
        "cinematic tarot reading table, three major arcana cards laid out, "
        f"{cards}, mystical gold candlelight, dark forest temple, "
        "photorealistic, no letters, no watermark, vertical altar composition"
    )


async def generate_scene(spread: Spread) -> bytes | None:
    prompt = quote(scene_prompt(spread)[:380])
    url = (
        f"https://image.pollinations.ai/prompt/{prompt}"
        "?width=1024&height=768&nologo=true&model=flux"
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
