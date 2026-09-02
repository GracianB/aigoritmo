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
        "bg": (8, 16, 12),
        "card": (16, 38, 28),
        "gold": (214, 178, 96),
        "text": (240, 232, 204),
        "mute": (156, 174, 154),
        "edge": (92, 158, 114),
        "ink": (6, 12, 10),
    },
    "arcano": {
        "bg": (8, 12, 24),
        "card": (20, 30, 54),
        "gold": (198, 166, 96),
        "text": (230, 234, 246),
        "mute": (144, 156, 184),
        "edge": (82, 138, 188),
        "ink": (6, 8, 18),
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
                "Nómbrala. Di qué se ve. Relaciónala con la pregunta en 5 a 8 frases cortas, para oírse en voz alta.",
                "Español concreto, adulto, sin markdown, sin viñetas, sin consejo médico, legal ni financiero.",
            ]
        )


def draw_spread(question: str, avatar_id: str) -> Spread:
    seed = hashlib.sha256(f"{avatar_id}|{question.strip().lower()}".encode("utf-8")).hexdigest()
    rng = random.Random(seed)
    roman, name, keywords = rng.choice(MAJOR_ARCANA)
    card = DrawnCard(roman=roman, name=name, keywords=keywords, position="Carta")
    return Spread(question=question.strip(), cards=(card,), avatar_id=avatar_id)


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    windows = Path(r"C:\Windows\Fonts")
    if bold:
        names = ["georgiab.ttf", "segoeuib.ttf", "arialbd.ttf", "timesbd.ttf", "georgia.ttf", "segoeui.ttf"]
    else:
        names = ["georgia.ttf", "segoeui.ttf", "arial.ttf", "times.ttf", "calibri.ttf"]
    for name in names:
        path = windows / name
        if path.is_file():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                continue
    return ImageFont.load_default()


def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _center(draw: ImageDraw.ImageDraw, y: int, text: str, font: ImageFont.ImageFont, fill: tuple[int, int, int], width: int) -> int:
    w, h = _text_size(draw, text, font)
    draw.text(((width - w) / 2, y), text, font=font, fill=fill)
    return h


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        w, _ = _text_size(draw, trial, font)
        if w <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _diamond(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, fill: tuple[int, int, int]) -> None:
    draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], outline=fill)


def render_spread(spread: Spread) -> bytes:
    palette = PALETTES.get(spread.avatar_id, PALETTES["arcana"])
    width, height = 768, 1280
    image = Image.new("RGB", (width, height), palette["bg"])
    draw = ImageDraw.Draw(image)
    title_font = _font(26, bold=True)
    card_title = _font(40, bold=True)
    roman_font = _font(86, bold=True)
    body_font = _font(22)
    small_font = _font(16)
    card = spread.cards[0]

    header = "ARCANA" if spread.avatar_id == "arcana" else "ARCANO"
    outer = (36, 36, width - 36, height - 36)
    draw.rounded_rectangle(outer, radius=40, fill=palette["card"], outline=palette["gold"], width=8)
    inner = (58, 58, width - 58, height - 58)
    draw.rounded_rectangle(inner, radius=28, outline=palette["edge"], width=2)
    filigree = (78, 78, width - 78, height - 78)
    draw.rounded_rectangle(filigree, radius=20, outline=palette["gold"], width=1)

    _diamond(draw, 96, 96, 9, palette["gold"])
    _diamond(draw, width - 96, 96, 9, palette["gold"])
    _diamond(draw, 96, height - 96, 9, palette["gold"])
    _diamond(draw, width - 96, height - 96, 9, palette["gold"])

    cx, cy = width // 2, 430
    draw.ellipse((cx - 132, cy - 132, cx + 132, cy + 132), outline=palette["edge"], width=1)
    draw.ellipse((cx - 118, cy - 118, cx + 118, cy + 118), outline=palette["gold"], width=1)

    _center(draw, 128, header, title_font, palette["gold"], width)
    _center(draw, 172, "UNA CARTA  ·  ARCANO MAYOR", small_font, palette["mute"], width)
    draw.line((int(width * 0.30), 218, int(width * 0.70), 218), fill=palette["gold"], width=1)

    _center(draw, 330, card.roman, roman_font, palette["gold"], width)
    _center(draw, 448, card.name, card_title, palette["text"], width)
    keywords = " · ".join(part.strip() for part in card.keywords.split(",") if part.strip())
    _center(draw, 516, keywords, body_font, palette["mute"], width)

    draw.line((int(width * 0.30), height - 250, int(width * 0.70), height - 250), fill=palette["edge"], width=1)
    _center(draw, height - 228, "la pregunta", small_font, palette["mute"], width)
    y = height - 196
    for line in _wrap(draw, spread.question, body_font, width - 200)[:4]:
        _center(draw, y, line, body_font, palette["text"], width)
        y += 30

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()