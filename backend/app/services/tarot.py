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
    cards: tuple[DrawnCard, ...]
    avatar_id: str

    def briefing(self) -> str:
        card = self.cards[0]
        return "\n".join(
            [
                f"Pregunta del consultante: {self.question}",
                "Tirada de UN solo arcano mayor. Interpreta SOLO esta carta. Nunca hables de tres cartas ni de pasado/presente/futuro:",
                f"- {card.roman} {card.name} ({card.keywords})",
                "Relaciónala con la pregunta. Español, concreto, sin relleno.",
            ]
        )


def draw_spread(question: str, avatar_id: str) -> Spread:
    seed = hashlib.sha256(f"{avatar_id}|{question.strip().lower()}".encode("utf-8")).hexdigest()
    rng = random.Random(seed)
    roman, name, keywords = rng.choice(MAJOR_ARCANA)
    card = DrawnCard(roman=roman, name=name, keywords=keywords, position="Carta")
    return Spread(question=question.strip(), cards=(card,), avatar_id=avatar_id)


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
    width, height = 768, 1280
    image = Image.new("RGB", (width, height), palette["bg"])
    draw = ImageDraw.Draw(image)
    title_font = _font(28, bold=True)
    card_title = _font(36, bold=True)
    roman_font = _font(72, bold=True)
    body_font = _font(22)
    small_font = _font(18)
    card = spread.cards[0]

    header = "ARCANA" if spread.avatar_id == "arcana" else "ARCANO"
    outer = (28, 28, width - 28, height - 28)
    draw.rounded_rectangle(outer, radius=36, fill=palette["card"], outline=palette["gold"], width=7)
    inner = (52, 52, width - 52, height - 52)
    draw.rounded_rectangle(inner, radius=24, outline=palette["edge"], width=2)
    filigree = (72, 72, width - 72, height - 72)
    draw.rounded_rectangle(filigree, radius=18, outline=palette["gold"], width=1)

    draw.text((96, 110), header, font=title_font, fill=palette["gold"])
    draw.text((96, 160), "Una carta", font=small_font, fill=palette["mute"])
    draw.text((96, 360), card.roman, font=roman_font, fill=palette["gold"])
    draw.text((96, 470), card.name, font=card_title, fill=palette["text"])
    draw.text((96, 540), card.keywords, font=body_font, fill=palette["mute"])

    q = spread.question
    if len(q) > 70:
        q = q[:67] + "…"
    draw.text((96, height - 160), q, font=body_font, fill=palette["text"])

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
