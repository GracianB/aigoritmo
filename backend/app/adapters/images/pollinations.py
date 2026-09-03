"""Free image generation via Pollinations (no API key). Demo-grade, not SLA."""
import hashlib
from urllib.parse import quote

import httpx

from app.services.tarot import Spread

PALETTE_EN = {
    "arcana": "candlelit garnet velvet, warm gold leaf, blood-red shadows, museum oil",
    "arcano": "moonlit steel-blue velvet, cold silver leaf, indigo shadows, museum oil",
}


def scene_prompt(spread: Spread) -> str:
    card = spread.cards[0]
    keywords = card.keywords.replace(",", ", ")
    palette = PALETTE_EN.get(spread.avatar_id, PALETTE_EN["arcana"])
    motif = card.motif_en.strip()
    return (
        "a single tarot card in classic tarot-card shape, vertical rectangular naipe "
        "with ornate filigree border and rounded corners, "
        f"major arcana {card.name} painted as the scene inside the card: {motif}, "
        f"symbolic motifs of {keywords}, {palette}, "
        "cinematic chiaroscuro oil on aged gesso, gallery lighting, adult, not cartoon, not childish, "
        "vintage tarot playing card filling the frame, one card only, no table, no extra cards, "
        "no letters, no watermark, no text, no caption, no typography"
    )


def scene_seed(spread: Spread) -> int:
    card = spread.cards[0]
    digest = hashlib.sha256(f"{spread.avatar_id}|{spread.question}|{card.name}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 999_999


async def generate_scene(spread: Spread) -> bytes | None:
    prompt = quote(scene_prompt(spread)[:480])
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
