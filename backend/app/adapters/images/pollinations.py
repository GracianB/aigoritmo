"""Free image generation via Pollinations (no API key). Demo-grade, not SLA."""
import hashlib
from urllib.parse import quote

import httpx

from app.services.tarot import Spread


def scene_prompt(spread: Spread) -> str:
    card = spread.cards[0]
    keywords = card.keywords.replace(",", ", ")
    return (
        "a single tarot card in classic tarot-card shape, vertical rectangular naipe "
        "with ornate gold filigree border and rounded corners, "
        f"major arcana {card.name} as the painted scene inside the card, "
        f"symbolic motifs of {keywords}, "
        "cinematic chiaroscuro oil painting, candlelit, adult, not cartoon, not childish, "
        "vintage tarot playing card, one card only, no table, no extra cards, "
        "mystical dark background, no letters, no watermark, no text"
    )


def scene_seed(spread: Spread) -> int:
    card = spread.cards[0]
    digest = hashlib.sha256(f"{spread.avatar_id}|{spread.question}|{card.name}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 999_999


async def generate_scene(spread: Spread) -> bytes | None:
    prompt = quote(scene_prompt(spread)[:420])
    seed = scene_seed(spread)
    url = (
        f"https://image.pollinations.ai/prompt/{prompt}"
        f"?width=768&height=1280&nologo=true&model=flux&seed={seed}"
    )
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(8.0, connect=3.0), follow_redirects=True) as client:
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