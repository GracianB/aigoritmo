from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

MAJOR_ARCANA: list[tuple[str, str, str, str, str]] = [
    ("0", "El Loco", "inicio, salto, inocencia", "un joven al borde, saco al hombro, perro a los talones", "youth at a sunlit cliff, bindle on a stick, small dog, white rose"),
    ("I", "El Mago", "voluntad, oficio, foco", "una mesa de oficios, varita alzada, infinito sobre la cabeza", "magician at a work table, raised wand, lemniscate, roses and lilies"),
    ("II", "La Sacerdotisa", "intuición, secreto, espera", "entre dos columnas, libro cerrado, luna a los pies", "high priestess between pillars, veiled book, crescent moon at her feet"),
    ("III", "La Emperatriz", "nutrir, abundancia, cuerpo", "trono en un jardín, trigo, corona de estrellas", "empress on a garden throne, wheat, starry crown, ripe orchard"),
    ("IV", "El Emperador", "orden, límite, autoridad", "trono de piedra, armadura, montañas secas", "emperor on a stone throne, armor, ram motif, barren mountains"),
    ("V", "El Hierofante", "tradición, guía, rito", "dos llaves cruzadas, dos discípulos, bendicion", "hierophant with crossed keys, two acolytes, raised blessing"),
    ("VI", "Los Enamorados", "elección, vínculo, deseo", "dos cuerpos bajo un sol, un angel, un arbol", "two lovers under a radiant sun, an angel above, a tree of flame"),
    ("VII", "El Carro", "avance, dominio, direccion", "un carro de piedra, dos esfinges, ciudad atras", "stone chariot drawn by two sphinxes, canopy of stars, city behind"),
    ("VIII", "La Justicia", "verdad, equilibrio, consecuencia", "espada y balanza, mirada fija, manto rojo", "justice seated, upright sword and scales, red mantle, steady gaze"),
    ("IX", "El Ermitaño", "retiro, búsqueda, lámpara", "un farol en la nieve, capa, montana", "hermit on a mountain path, lantern with a star, winter cloak"),
    ("X", "La Rueda", "ciclo, giro, timing", "una rueda con criaturas, nubes, giro", "wheel of fortune in the clouds, rising and falling creatures, turning axle"),
    ("XI", "La Fuerza", "coraje suave, pulso, dominio", "una mujer cierra las fauces de un leon", "woman gently closing a lion's jaws, infinity over her head, flowers"),
    ("XII", "El Colgado", "pausa, otra mirada, entrega", "un hombre invertido, halo, arbol en tau", "hanged man suspended from a tau cross, calm face, golden halo"),
    ("XIII", "La Muerte", "cierre, muda, corte", "un jinete de armadura oscura, rosa blanca, sol bajo el horizonte", "armored rider on a pale horse, white rose banner, sun setting"),
    ("XIV", "La Templanza", "mezcla, ritmo, sanar", "un angel vierte agua entre dos copas, un pie en el rio", "angel pouring between two cups, one foot in a river, rising sun"),
    ("XV", "El Diablo", "atadura, sombra, apetito", "una figura cornuda, dos atados, antorcha invertida", "horned figure on a plinth, two bound figures, inverted torch"),
    ("XVI", "La Torre", "quiebre, revelacion, caida", "una torre herida por un rayo, corona que cae, fuego", "stone tower struck by lightning, falling crown, flame from windows"),
    ("XVII", "La Estrella", "fe, alivio, norte", "una mujer desnuda vierte agua, una estrella grande, un ibis", "kneeling woman pouring water, large eight-pointed star, ibis in a tree"),
    ("XVIII", "La Luna", "confusión, sueño, miedo", "un camino entre dos torres, un cangrejo, dos perros", "path between two towers, crayfish in water, moon face, two howling dogs"),
    ("XIX", "El Sol", "claridad, gozo, éxito", "un nino en un caballo blanco, girasoles, un sol enorme", "child on a white horse, sunflowers, enormous radiant sun"),
    ("XX", "El Juicio", "llamada, despertar, cuenta", "un angel con trompeta, figuras que se alzan", "angel with trumpet, figures rising from the earth, banner cross"),
    ("XXI", "El Mundo", "cierre pleno, integracion", "una figura en una guirnalda, cuatro criaturas en las esquinas", "dancing figure in a laurel wreath, four living creatures at the corners"),
]


PALETTES = {
    "arcana": {
        "bg": (10, 6, 8),
        "velvet": (36, 12, 18),
        "card": (48, 16, 24),
        "mat": (28, 12, 16),
        "gold": (214, 181, 122),
        "gold_lit": (239, 212, 163),
        "text": (243, 234, 209),
        "mute": (176, 148, 118),
        "edge": (122, 36, 51),
        "ink": (14, 8, 10),
        "parchment": (42, 28, 24),
    },
    "arcano": {
        "bg": (6, 10, 16),
        "velvet": (14, 22, 34),
        "card": (18, 28, 44),
        "mat": (12, 18, 30),
        "gold": (158, 180, 200),
        "gold_lit": (212, 227, 239),
        "text": (230, 236, 244),
        "mute": (140, 156, 176),
        "edge": (74, 104, 132),
        "ink": (6, 8, 16),
        "parchment": (20, 28, 40),
    },
}


@dataclass(frozen=True)
class DrawnCard:
    roman: str
    name: str
    keywords: str
    position: str
    motif: str
    motif_en: str


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
                f"Lo que se ve en la lámina: {card.motif}.",
                "Cómo lees, en este orden, 6 a 8 frases cortas para oírse en voz alta:",
                "Nombra la carta. Di qué se ve. Relaciónala con la pregunta como si hablaras al oído. Ofrece una imagen concreta de su vida. Distingue lo que observas de lo que interpretas. Cierra con una pregunta, nunca con un veredicto.",
                "Español concreto, adulto, íntimo, sin markdown, sin viñetas, sin consejo médico, legal ni financiero.",
            ]
        )


def draw_spread(question: str, avatar_id: str) -> Spread:
    seed = hashlib.sha256(f"{avatar_id}|{question.strip().lower()}".encode("utf-8")).hexdigest()
    rng = random.Random(seed)
    roman, name, keywords, motif, motif_en = rng.choice(MAJOR_ARCANA)
    card = DrawnCard(
        roman=roman,
        name=name,
        keywords=keywords,
        position=roman,
        motif=motif,
        motif_en=motif_en,
    )
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


def _star(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, points: int, fill: tuple[int, int, int]) -> None:
    coords: list[tuple[float, float]] = []
    for i in range(points * 2):
        ang = math.pi / 2 + i * math.pi / points
        rad = r if i % 2 == 0 else r * 0.42
        coords.append((cx + rad * math.cos(ang), cy - rad * math.sin(ang)))
    draw.polygon(coords, outline=fill)


def _emblem(draw: ImageDraw.ImageDraw, roman: str, cx: int, cy: int, gold: tuple[int, int, int], edge: tuple[int, int, int]) -> None:
    draw.ellipse((cx - 118, cy - 118, cx + 118, cy + 118), outline=edge, width=1)
    draw.ellipse((cx - 104, cy - 104, cx + 104, cy + 104), outline=gold, width=2)
    draw.ellipse((cx - 92, cy - 92, cx + 92, cy + 92), outline=edge, width=1)
    if roman in {"0"}:
        draw.arc((cx - 36, cy - 10, cx + 50, cy + 48), 200, 20, fill=gold, width=3)
        draw.ellipse((cx + 28, cy - 48, cx + 52, cy - 24), outline=gold, width=2)
        draw.line((cx - 8, cy + 8, cx + 22, cy - 18), fill=gold, width=3)
    elif roman == "I":
        draw.line((cx, cy - 52, cx, cy + 44), fill=gold, width=4)
        draw.arc((cx - 28, cy - 70, cx + 28, cy - 28), 20, 160, fill=gold, width=2)
        draw.arc((cx - 28, cy - 58, cx + 28, cy - 16), 200, 340, fill=gold, width=2)
        draw.rectangle((cx - 40, cy + 44, cx + 40, cy + 52), outline=gold, width=2)
    elif roman == "II":
        draw.arc((cx - 58, cy - 18, cx - 6, cy + 34), 200, 20, fill=gold, width=3)
        draw.arc((cx + 6, cy - 18, cx + 58, cy + 34), 160, 340, fill=gold, width=3)
        draw.line((cx - 18, cy - 48, cx - 18, cy + 48), fill=edge, width=2)
        draw.line((cx + 18, cy - 48, cx + 18, cy + 48), fill=edge, width=2)
    elif roman == "III":
        draw.ellipse((cx - 16, cy - 28, cx + 16, cy + 4), outline=gold, width=3)
        draw.line((cx, cy + 4, cx, cy + 48), fill=gold, width=3)
        draw.line((cx - 22, cy + 22, cx + 22, cy + 22), fill=gold, width=3)
        _star(draw, cx, cy - 48, 10, 8, gold)
    elif roman == "IV":
        draw.rectangle((cx - 42, cy - 18, cx + 42, cy + 42), outline=gold, width=3)
        draw.polygon([(cx - 42, cy - 18), (cx, cy - 52), (cx + 42, cy - 18)], outline=gold)
    elif roman == "V":
        draw.line((cx - 28, cy - 8, cx + 28, cy + 36), fill=gold, width=3)
        draw.line((cx + 28, cy - 8, cx - 28, cy + 36), fill=gold, width=3)
        draw.ellipse((cx - 10, cy - 48, cx + 10, cy - 28), outline=gold, width=2)
        draw.line((cx - 36, cy - 48, cx - 36, cy + 48), fill=edge, width=2)
        draw.line((cx + 36, cy - 48, cx + 36, cy + 48), fill=edge, width=2)
    elif roman == "VI":
        draw.line((cx - 28, cy - 8, cx - 28, cy + 40), fill=gold, width=3)
        draw.line((cx + 28, cy - 8, cx + 28, cy + 40), fill=gold, width=3)
        draw.ellipse((cx - 38, cy - 36, cx - 18, cy - 16), outline=gold, width=2)
        draw.ellipse((cx + 18, cy - 36, cx + 38, cy - 16), outline=gold, width=2)
        _star(draw, cx, cy - 58, 12, 8, gold)
    elif roman == "VII":
        draw.polygon([(cx - 46, cy + 8), (cx - 30, cy - 28), (cx + 30, cy - 28), (cx + 46, cy + 8)], outline=gold)
        draw.ellipse((cx - 38, cy + 12, cx - 14, cy + 36), outline=gold, width=2)
        draw.ellipse((cx + 14, cy + 12, cx + 38, cy + 36), outline=gold, width=2)
    elif roman == "VIII":
        draw.line((cx, cy - 40, cx, cy + 48), fill=gold, width=3)
        draw.line((cx - 40, cy - 18, cx + 40, cy - 18), fill=gold, width=3)
        draw.ellipse((cx - 48, cy - 36, cx - 24, cy - 12), outline=gold, width=2)
        draw.ellipse((cx + 24, cy - 36, cx + 48, cy - 12), outline=gold, width=2)
        draw.polygon([(cx - 10, cy + 20), (cx, cy + 52), (cx + 10, cy + 20)], outline=gold)
    elif roman == "IX":
        draw.polygon([(cx, cy - 52), (cx + 22, cy - 18), (cx, cy + 8), (cx - 22, cy - 18)], outline=gold)
        draw.ellipse((cx - 8, cy - 36, cx + 8, cy - 20), outline=gold, width=2)
        draw.line((cx, cy + 8, cx, cy + 48), fill=gold, width=3)
    elif roman == "X":
        draw.ellipse((cx - 48, cy - 48, cx + 48, cy + 48), outline=gold, width=3)
        draw.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), outline=gold, width=2)
        for i in range(8):
            ang = i * math.pi / 4
            draw.line((cx, cy, cx + 48 * math.cos(ang), cy + 48 * math.sin(ang)), fill=gold, width=2)
    elif roman == "XI":
        draw.arc((cx - 34, cy - 58, cx, cy - 16), 20, 160, fill=gold, width=2)
        draw.arc((cx, cy - 58, cx + 34, cy - 16), 200, 340, fill=gold, width=2)
        draw.arc((cx - 40, cy - 8, cx + 40, cy + 52), 200, 20, fill=gold, width=3)
        draw.ellipse((cx - 16, cy + 8, cx + 16, cy + 40), outline=gold, width=2)
    elif roman == "XII":
        draw.polygon([(cx, cy + 48), (cx - 36, cy - 20), (cx + 36, cy - 20)], outline=gold)
        draw.line((cx, cy - 48, cx, cy - 20), fill=gold, width=3)
        draw.ellipse((cx - 8, cy + 8, cx + 8, cy + 24), outline=gold, width=2)
    elif roman == "XIII":
        draw.line((cx - 8, cy - 48, cx - 8, cy + 36), fill=gold, width=3)
        draw.polygon([(cx - 8, cy - 36), (cx + 44, cy - 20), (cx - 8, cy - 8)], outline=gold)
        draw.arc((cx - 36, cy + 16, cx + 20, cy + 56), 20, 200, fill=gold, width=3)
    elif roman == "XIV":
        draw.arc((cx - 44, cy - 8, cx - 8, cy + 40), 200, 20, fill=gold, width=3)
        draw.arc((cx + 8, cy - 8, cx + 44, cy + 40), 200, 20, fill=gold, width=3)
        draw.line((cx - 26, cy - 8, cx + 26, cy + 8), fill=gold, width=2)
        draw.ellipse((cx - 10, cy - 52, cx + 10, cy - 32), outline=gold, width=2)
    elif roman == "XV":
        draw.polygon([(cx, cy - 52), (cx + 18, cy - 8), (cx, cy + 8), (cx - 18, cy - 8)], outline=gold)
        draw.line((cx - 28, cy + 16, cx - 28, cy + 48), fill=gold, width=2)
        draw.line((cx + 28, cy + 16, cx + 28, cy + 48), fill=gold, width=2)
        draw.arc((cx - 40, cy + 28, cx - 16, cy + 52), 0, 180, fill=gold, width=2)
        draw.arc((cx + 16, cy + 28, cx + 40, cy + 52), 0, 180, fill=gold, width=2)
    elif roman == "XVI":
        draw.rectangle((cx - 22, cy - 8, cx + 22, cy + 52), outline=gold, width=3)
        draw.polygon([(cx - 22, cy - 8), (cx, cy - 36), (cx + 22, cy - 8)], outline=gold)
        draw.line((cx - 48, cy - 52, cx + 8, cy - 8), fill=gold, width=3)
        draw.line((cx - 20, cy - 44, cx - 8, cy - 28), fill=gold, width=2)
    elif roman == "XVII":
        _star(draw, cx, cy - 12, 36, 8, gold)
        draw.ellipse((cx - 6, cy - 18, cx + 6, cy - 6), outline=gold, width=2)
        draw.line((cx - 28, cy + 36, cx + 28, cy + 36), fill=gold, width=2)
    elif roman == "XVIII":
        draw.arc((cx - 36, cy - 40, cx + 28, cy + 28), 40, 280, fill=gold, width=3)
        draw.ellipse((cx + 10, cy - 8, cx + 22, cy + 4), outline=gold, width=2)
        draw.ellipse((cx - 48, cy + 28, cx - 32, cy + 44), outline=edge, width=2)
        draw.ellipse((cx + 32, cy + 28, cx + 48, cy + 44), outline=edge, width=2)
    elif roman == "XIX":
        draw.ellipse((cx - 28, cy - 28, cx + 28, cy + 28), outline=gold, width=3)
        for i in range(12):
            ang = i * math.pi / 6
            draw.line(
                (cx + 34 * math.cos(ang), cy + 34 * math.sin(ang), cx + 52 * math.cos(ang), cy + 52 * math.sin(ang)),
                fill=gold,
                width=2,
            )
    elif roman == "XX":
        draw.polygon([(cx - 8, cy - 48), (cx + 8, cy - 48), (cx + 8, cy - 8), (cx + 36, cy + 8), (cx - 8, cy - 8)], outline=gold)
        draw.arc((cx - 40, cy + 8, cx + 40, cy + 52), 200, 340, fill=gold, width=3)
        draw.line((cx - 24, cy + 40, cx - 24, cy + 52), fill=gold, width=2)
        draw.line((cx + 24, cy + 40, cx + 24, cy + 52), fill=gold, width=2)
    else:
        draw.ellipse((cx - 52, cy - 40, cx + 52, cy + 48), outline=gold, width=3)
        draw.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), outline=gold, width=2)
        _star(draw, cx, cy, 8, 4, gold)


def render_spread(spread: Spread) -> bytes:
    palette = PALETTES.get(spread.avatar_id, PALETTES["arcana"])
    width, height = 768, 1280
    image = Image.new("RGB", (width, height), palette["bg"])
    draw = ImageDraw.Draw(image)

    # Velvet wash
    wash = Image.new("RGB", (width, height), palette["bg"])
    wash_draw = ImageDraw.Draw(wash)
    wash_draw.ellipse((-120, 80, width + 120, height - 40), fill=palette["velvet"])
    image = Image.blend(image, wash.filter(ImageFilter.GaussianBlur(48)), 0.72)
    draw = ImageDraw.Draw(image)

    title_font = _font(22, bold=True)
    card_title = _font(42, bold=True)
    roman_font = _font(78, bold=True)
    body_font = _font(22)
    small_font = _font(15)
    italic_guess = _font(20)
    card = spread.cards[0]
    house = "ARCANA" if spread.avatar_id == "arcana" else "ARCANO"

    outer = (28, 28, width - 28, height - 28)
    draw.rounded_rectangle(outer, radius=36, fill=palette["card"], outline=palette["gold"], width=10)
    mat = (48, 48, width - 48, height - 48)
    draw.rounded_rectangle(mat, radius=28, fill=palette["mat"], outline=palette["gold_lit"], width=2)
    inner = (68, 68, width - 68, height - 68)
    draw.rounded_rectangle(inner, radius=22, outline=palette["edge"], width=1)
    plate = (88, 88, width - 88, height - 88)
    draw.rounded_rectangle(plate, radius=16, fill=palette["parchment"], outline=palette["gold"], width=1)

    for dx, dy in ((112, 112), (width - 112, 112), (112, height - 112), (width - 112, height - 112)):
        _diamond(draw, dx, dy, 8, palette["gold"])
        _diamond(draw, dx, dy, 4, palette["gold_lit"])

    _center(draw, 118, house, title_font, palette["gold"], width)
    _center(draw, 150, "UN ARCANO MAYOR", small_font, palette["mute"], width)
    draw.line((int(width * 0.32), 188, int(width * 0.68), 188), fill=palette["gold"], width=1)

    _center(draw, 214, card.roman, roman_font, palette["gold_lit"], width)
    _emblem(draw, card.roman, width // 2, 430, palette["gold"], palette["edge"])
    _center(draw, 568, card.name, card_title, palette["text"], width)

    keywords = "  ·  ".join(part.strip() for part in card.keywords.split(",") if part.strip())
    _center(draw, 628, keywords, body_font, palette["mute"], width)

    draw.line((int(width * 0.28), height - 268, int(width * 0.72), height - 268), fill=palette["edge"], width=1)
    _center(draw, height - 248, "la consulta", small_font, palette["mute"], width)
    y = height - 214
    for line in _wrap(draw, spread.question, italic_guess, width - 220)[:4]:
        _center(draw, y, line, italic_guess, palette["text"], width)
        y += 32

    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()
