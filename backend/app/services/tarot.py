from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

MAJOR_ARCANA: list[tuple[str, str, str]] = [
    ("0", "El Loco", "inicio, salto, inocencia"),
    ("I", "El Mago", "voluntad, oficio, foco"),
    ("II", "La Sacerdotisa", "intuición, secreto, espera"),
    ("III", "La Emperatriz", "nutrir, abundancia, cuerpo"),
    ("IV", "El Emperador", "orden, límite, autoridad"),
    ("V", "El Hierofante", "tradición, guía, rito"),
    ("VI", "Los Enamorados", "elección, vínculo, deseo"),
    ("VII", "El Carro", "avance, dominio, dirección"),
    ("VIII", "La Justicia", "verdad, equilibrio, consecuencia"),
    ("IX", "El Ermitaño", "retiro, búsqueda, lámpara"),
    ("X", "La Rueda", "ciclo, giro, timing"),
    ("XI", "La Fuerza", "coraje suave, pulso, dominio"),
    ("XII", "El Colgado", "pausa, otra mirada, entrega"),
    ("XIII", "La Muerte", "cierre, muda, corte"),
    ("XIV", "La Templanza", "mezcla, ritmo, sanar"),
    ("XV", "El Diablo", "atadura, sombra, apetito"),
    ("XVI", "La Torre", "quiebre, revelación, caída"),
    ("XVII", "La Estrella", "fe, alivio, norte"),
    ("XVIII", "La Luna", "confusión, sueño, miedo"),
    ("XIX", "El Sol", "claridad, gozo, éxito"),
    ("XX", "El Juicio", "llamada, despertar, cuenta"),
    ("XXI", "El Mundo", "cierre pleno, integración"),
]

POSITIONS = ("Pasado", "Presente", "Futuro")

PALETTES = {
    "arcana": {
        "bg": (8, 18, 14),
        "card": (18, 42, 32),
        "gold": (212, 175, 90),
        "text": (236, 228, 196),
        "mute": (150, 168, 148),
        "edge": (90, 160, 110),
    },
    "arcano": {
        "bg": (10, 14, 28),
        "card": (22, 32, 58),
        "gold": (196, 164, 92),
        "text": (228, 232, 245),
        "mute": (140, 152, 180),
        "edge": (80, 140, 190),
    },
}


@dataclass(frozen=True)
class DrawnCard:
    roman: str
    name: str
    keywords: str
    position: str


@dataclass(frozen=True)
class Spread:
    question: str
    cards: tuple[DrawnCard, DrawnCard, DrawnCard]
    avatar_id: str

    def briefing(self) -> str:
        lines = [
            f"Pregunta del consultante: {self.question}",
            "Tirada de tres arcanos mayores (úsalas SOLO estas, no inventes otras):",
        ]
        for card in self.cards:
            lines.append(f"- {card.position}: {card.roman} {card.name} ({card.keywords})")
        lines.append(
            "Interpreta cada carta en relación directa con la pregunta. "
            "Luego una síntesis clara. Español, concreto, sin relleno."
        )
        return "\n".join(lines)


def draw_spread(question: str, avatar_id: str) -> Spread:
    seed = hashlib.sha256(f"{avatar_id}|{question.strip().lower()}".encode("utf-8")).hexdigest()
    rng = random.Random(seed)
    picks = rng.sample(MAJOR_ARCANA, 3)
    cards = tuple(
        DrawnCard(roman=p[0], name=p[1], keywords=p[2], position=POSITIONS[i])
        for i, p in enumerate(picks)
    )
    return Spread(question=question.strip(), cards=cards, avatar_id=avatar_id)


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = [
        "segoeui.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
        "arial.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
    ]
    windows = Path(r"C:\Windows\Fonts")
    for name in names:
        path = windows / name
        if path.is_file():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                continue
    return ImageFont.load_default()


def render_spread(spread: Spread) -> bytes:
    palette = PALETTES.get(spread.avatar_id, PALETTES["arcana"])
    width, height = 1200, 780
    image = Image.new("RGB", (width, height), palette["bg"])
    draw = ImageDraw.Draw(image)
    title_font = _font(28, bold=True)
    card_title = _font(26, bold=True)
    roman_font = _font(42, bold=True)
    body_font = _font(18)
    small_font = _font(16)

    header = "ARCANA" if spread.avatar_id == "arcana" else "ARCANO"
    draw.text((48, 28), header, font=title_font, fill=palette["gold"])
    draw.text((48, 68), "Tirada de tres caminos", font=small_font, fill=palette["mute"])

    card_w, card_h = 320, 480
    gap = 40
    start_x = (width - (card_w * 3 + gap * 2)) // 2
    top = 120
    for i, card in enumerate(spread.cards):
        x = start_x + i * (card_w + gap)
        box = (x, top, x + card_w, top + card_h)
        draw.rounded_rectangle(box, radius=18, fill=palette["card"], outline=palette["edge"], width=3)
        inner = (x + 14, top + 14, x + card_w - 14, top + card_h - 14)
        draw.rounded_rectangle(inner, radius=12, outline=palette["gold"], width=1)
        draw.text((x + 24, top + 28), card.position.upper(), font=small_font, fill=palette["gold"])
        draw.text((x + 24, top + 120), card.roman, font=roman_font, fill=palette["gold"])
        draw.text((x + 24, top + 190), card.name, font=card_title, fill=palette["text"])
        draw.text((x + 24, top + 250), card.keywords, font=body_font, fill=palette["mute"])

    q = spread.question
    if len(q) > 110:
        q = q[:107] + "…"
    draw.rectangle((0, height - 90, width, height), fill=(0, 0, 0))
    draw.text((48, height - 58), f"Pregunta: {q}", font=body_font, fill=palette["text"])

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
