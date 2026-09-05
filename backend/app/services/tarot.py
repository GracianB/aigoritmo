from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

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
        "bg": (8, 4, 6),
        "velvet": (42, 10, 18),
        "velvet_lit": (64, 18, 28),
        "card": (52, 14, 22),
        "mat": (30, 10, 16),
        "gold": (214, 181, 122),
        "gold_lit": (242, 216, 168),
        "gold_dim": (148, 110, 68),
        "text": (246, 236, 214),
        "mute": (176, 148, 118),
        "edge": (128, 34, 48),
        "ink": (12, 6, 8),
        "parchment": (46, 26, 22),
        "parchment_lit": (62, 36, 30),
        "shadow": (4, 2, 3),
        "glow": (180, 90, 70),
    },
    "arcano": {
        "bg": (4, 8, 14),
        "velvet": (12, 22, 38),
        "velvet_lit": (22, 36, 56),
        "card": (16, 26, 42),
        "mat": (10, 16, 28),
        "gold": (158, 180, 200),
        "gold_lit": (216, 230, 242),
        "gold_dim": (96, 118, 140),
        "text": (232, 238, 246),
        "mute": (140, 156, 176),
        "edge": (70, 100, 130),
        "ink": (4, 6, 14),
        "parchment": (18, 26, 38),
        "parchment_lit": (28, 38, 54),
        "shadow": (2, 4, 8),
        "glow": (80, 120, 160),
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


def _center_shadow(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    shadow: tuple[int, int, int],
    width: int,
    dx: int = 2,
    dy: int = 2,
) -> int:
    w, h = _text_size(draw, text, font)
    x = (width - w) / 2
    draw.text((x + dx, y + dy), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)
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


def _lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def _vertical_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    width, height = size
    strip = Image.new("RGB", (1, height))
    pix = strip.load()
    last = height - 1 or 1
    for y in range(height):
        pix[0, y] = _lerp(top, bottom, y / last)
    return strip.resize(size, Image.Resampling.BILINEAR)


def _soft_light(size: tuple[int, int], palette: dict[str, tuple[int, int, int]]) -> Image.Image:
    """One downscaled wash+glow+vignette pass instead of several full-res blurs."""
    w, h = size
    small = (max(w // 8, 1), max(h // 8, 1))
    layer = Image.new("RGB", small, palette["bg"])
    d = ImageDraw.Draw(layer)
    d.ellipse((-8, 2, small[0] + 8, small[1] - 1), fill=palette["velvet_lit"])
    d.ellipse((int(small[0] * 0.18), int(small[1] * 0.16), int(small[0] * 0.82), int(small[1] * 0.48)), fill=palette["glow"])
    # center medallion glow
    d.ellipse((int(small[0] * 0.32), int(small[1] * 0.28), int(small[0] * 0.68), int(small[1] * 0.46)), fill=palette["gold_dim"])
    # vignette dark corners
    edge = palette["shadow"]
    d.rectangle((0, 0, small[0], 2), fill=edge)
    d.rectangle((0, small[1] - 3, small[0], small[1]), fill=edge)
    d.rectangle((0, 0, 2, small[1]), fill=edge)
    d.rectangle((small[0] - 3, 0, small[0], small[1]), fill=edge)
    return layer.resize(size, Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(6))


def _apply_grain(image: Image.Image, seed: int, amount: float = 0.06) -> Image.Image:
    # Tiny noise tile, upscaled — far cheaper than full-frame effect_noise.
    rng = random.Random(seed)
    tw, th = 96, 160
    tile = Image.effect_noise((tw, th), 22.0)
    tile = ImageChops.offset(tile, rng.randint(0, tw - 1), rng.randint(0, th - 1))
    noise = tile.resize(image.size, Image.Resampling.BILINEAR)
    toned = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(image, toned, amount)



def _diamond(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, fill: tuple[int, int, int], width: int = 1) -> None:
    draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], outline=fill, width=width)


def _diamond_fill(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, fill: tuple[int, int, int]) -> None:
    draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=fill)


def _star(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, points: int, fill: tuple[int, int, int], width: int = 1) -> None:
    coords: list[tuple[float, float]] = []
    for i in range(points * 2):
        ang = math.pi / 2 + i * math.pi / points
        rad = r if i % 2 == 0 else r * 0.42
        coords.append((cx + rad * math.cos(ang), cy - rad * math.sin(ang)))
    draw.polygon(coords, outline=fill, width=width)


def _star_fill(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, points: int, fill: tuple[int, int, int]) -> None:
    coords: list[tuple[float, float]] = []
    for i in range(points * 2):
        ang = math.pi / 2 + i * math.pi / points
        rad = r if i % 2 == 0 else r * 0.42
        coords.append((cx + rad * math.cos(ang), cy - rad * math.sin(ang)))
    draw.polygon(coords, fill=fill)


def _box(x0: float, y0: float, x1: float, y1: float) -> tuple[float, float, float, float]:
    return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def _filigree_corner(draw: ImageDraw.ImageDraw, x: int, y: int, sx: int, sy: int, gold: tuple[int, int, int], lit: tuple[int, int, int], dim: tuple[int, int, int]) -> None:
    # Ornate corner flourish: nested scrolls + diamond studs. sx/sy mark inward direction.
    if sx > 0 and sy > 0:
        start, end = 180, 270
    elif sx < 0 and sy > 0:
        start, end = 270, 360
    elif sx > 0 and sy < 0:
        start, end = 90, 180
    else:
        start, end = 0, 90
    draw.arc(_box(x, y, x + 54 * sx, y + 54 * sy), start, end, fill=gold, width=2)
    draw.arc(_box(x + 8 * sx, y + 8 * sy, x + 40 * sx, y + 40 * sy), start, end, fill=dim, width=1)
    draw.line((x + 2 * sx, y + 56 * sy, x + 2 * sx, y + 18 * sy), fill=gold, width=2)
    draw.line((x + 56 * sx, y + 2 * sy, x + 18 * sx, y + 2 * sy), fill=gold, width=2)
    _diamond_fill(draw, x + 14 * sx, y + 14 * sy, 5, lit)
    _diamond(draw, x + 14 * sx, y + 14 * sy, 8, gold, 1)
    draw.ellipse(_box(x + 28 * sx - 3, y + 6 * sy - 3, x + 28 * sx + 3, y + 6 * sy + 3), fill=lit)
    draw.ellipse(_box(x + 6 * sx - 3, y + 28 * sy - 3, x + 6 * sx + 3, y + 28 * sy + 3), fill=lit)
    draw.arc(_box(x + 16 * sx, y + 30 * sy, x + 48 * sx, y + 52 * sy), 200, 340, fill=dim, width=1)
    draw.arc(_box(x + 30 * sx, y + 16 * sy, x + 52 * sx, y + 48 * sy), 110, 250, fill=dim, width=1)


def _side_flourish(draw: ImageDraw.ImageDraw, cx: int, y0: int, y1: int, gold: tuple[int, int, int], lit: tuple[int, int, int], left: bool) -> None:
    mid = (y0 + y1) // 2
    for yy in (mid - 90, mid, mid + 90):
        _diamond(draw, cx, yy, 6, gold, 1)
        _diamond_fill(draw, cx, yy, 3, lit)
        draw.line((cx, yy - 22, cx, yy - 8), fill=gold, width=1)
        draw.line((cx, yy + 8, cx, yy + 22), fill=gold, width=1)
        if left:
            draw.arc(_box(cx - 18, yy - 18, cx + 2, yy + 18), 90, 270, fill=gold, width=1)
        else:
            draw.arc(_box(cx - 2, yy - 18, cx + 18, yy + 18), 270, 90, fill=gold, width=1)


def _ornament_rule(draw: ImageDraw.ImageDraw, y: int, width: int, gold: tuple[int, int, int], lit: tuple[int, int, int], dim: tuple[int, int, int]) -> None:
    x0, x1 = int(width * 0.22), int(width * 0.78)
    draw.line((x0, y, x1, y), fill=dim, width=1)
    draw.line((x0 + 8, y - 1, x1 - 8, y - 1), fill=gold, width=1)
    cx = width // 2
    _diamond_fill(draw, cx, y, 5, lit)
    _diamond(draw, cx, y, 8, gold, 1)
    _diamond(draw, cx - 28, y, 3, gold, 1)
    _diamond(draw, cx + 28, y, 3, gold, 1)


def _medallion_ring(draw: ImageDraw.ImageDraw, cx: int, cy: int, gold: tuple[int, int, int], lit: tuple[int, int, int], edge: tuple[int, int, int], dim: tuple[int, int, int]) -> None:
    draw.ellipse((cx - 132, cy - 132, cx + 132, cy + 132), outline=dim, width=1)
    draw.ellipse((cx - 124, cy - 124, cx + 124, cy + 124), outline=gold, width=3)
    draw.ellipse((cx - 116, cy - 116, cx + 116, cy + 116), outline=lit, width=1)
    draw.ellipse((cx - 108, cy - 108, cx + 108, cy + 108), outline=edge, width=1)
    draw.ellipse((cx - 100, cy - 100, cx + 100, cy + 100), outline=gold, width=2)
    # Tick marks around the ring
    for i in range(24):
        ang = i * math.pi / 12
        r0, r1 = (118, 124) if i % 3 == 0 else (120, 124)
        draw.line(
            (cx + r0 * math.cos(ang), cy + r0 * math.sin(ang), cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)),
            fill=lit if i % 3 == 0 else dim,
            width=1,
        )
    for i in range(8):
        ang = math.pi / 8 + i * math.pi / 4
        _diamond_fill(draw, int(cx + 124 * math.cos(ang)), int(cy + 124 * math.sin(ang)), 3, lit)


def _emblem(draw: ImageDraw.ImageDraw, roman: str, cx: int, cy: int, gold: tuple[int, int, int], lit: tuple[int, int, int], edge: tuple[int, int, int], dim: tuple[int, int, int]) -> None:
    """Suggestive engraving / silhouette per Major Arcana — distinct at a glance."""
    _medallion_ring(draw, cx, cy, gold, lit, edge, dim)
    g, L, e, d = gold, lit, edge, dim

    if roman == "0":  # El Loco — cliff wanderer + dog
        draw.ellipse((cx - 14, cy - 58, cx + 10, cy - 34), outline=g, width=2)  # head
        draw.line((cx - 2, cy - 34, cx - 8, cy + 18), fill=g, width=3)  # body
        draw.line((cx - 8, cy - 8, cx - 36, cy + 8), fill=g, width=2)  # arm + stick
        draw.line((cx - 36, cy + 8, cx - 52, cy - 36), fill=L, width=2)
        draw.ellipse((cx - 58, cy - 48, cx - 46, cy - 36), outline=L, width=2)  # bindle
        draw.line((cx - 8, cy + 18, cx - 28, cy + 52), fill=g, width=2)
        draw.line((cx - 8, cy + 18, cx + 16, cy + 52), fill=g, width=2)
        draw.polygon([(cx - 70, cy + 56), (cx + 70, cy + 56), (cx + 40, cy + 72), (cx - 40, cy + 72)], outline=d)  # cliff
        draw.ellipse((cx + 28, cy + 36, cx + 52, cy + 56), outline=g, width=2)  # dog
        draw.line((cx + 50, cy + 40, cx + 62, cy + 28), fill=g, width=2)
    elif roman == "I":  # El Mago
        draw.line((cx, cy - 56, cx, cy + 36), fill=g, width=4)
        draw.ellipse((cx - 10, cy - 72, cx + 10, cy - 52), outline=L, width=2)
        draw.arc((cx - 30, cy - 78, cx + 30, cy - 34), 20, 160, fill=L, width=2)
        draw.arc((cx - 30, cy - 66, cx + 30, cy - 22), 200, 340, fill=L, width=2)
        draw.rectangle((cx - 48, cy + 40, cx + 48, cy + 56), outline=g, width=2)
        for ox in (-28, 0, 28):
            draw.ellipse((cx + ox - 6, cy + 44, cx + ox + 6, cy + 52), outline=L, width=1)
    elif roman == "II":  # La Sacerdotisa
        draw.line((cx - 48, cy - 64, cx - 48, cy + 64), fill=e, width=4)
        draw.line((cx + 48, cy - 64, cx + 48, cy + 64), fill=e, width=4)
        draw.arc((cx - 28, cy - 40, cx + 28, cy + 50), 200, 340, fill=g, width=3)
        draw.ellipse((cx - 12, cy - 62, cx + 12, cy - 38), outline=g, width=2)
        draw.arc((cx - 22, cy + 28, cx + 22, cy + 58), 20, 160, fill=L, width=2)  # moon
        draw.rectangle((cx - 18, cy - 8, cx + 18, cy + 22), outline=d, width=1)
    elif roman == "III":  # La Emperatriz
        draw.polygon([(cx - 50, cy + 50), (cx - 36, cy - 8), (cx + 36, cy - 8), (cx + 50, cy + 50)], outline=g, width=2)
        draw.ellipse((cx - 16, cy - 40, cx + 16, cy - 8), outline=g, width=2)
        _star_fill(draw, cx, cy - 56, 12, 8, L)
        for ox in (-30, -10, 10, 30):
            draw.ellipse((cx + ox - 4, cy + 34, cx + ox + 4, cy + 48), outline=d, width=1)
    elif roman == "IV":  # El Emperador
        draw.rectangle((cx - 46, cy - 10, cx + 46, cy + 52), outline=g, width=3)
        draw.polygon([(cx - 46, cy - 10), (cx, cy - 58), (cx + 46, cy - 10)], outline=L, width=2)
        draw.rectangle((cx - 14, cy + 8, cx + 14, cy + 36), outline=d, width=2)
        draw.polygon([(cx - 60, cy + 64), (cx, cy + 40), (cx + 60, cy + 64)], outline=e)
    elif roman == "V":  # El Hierofante
        draw.line((cx - 42, cy - 64, cx - 42, cy + 64), fill=e, width=3)
        draw.line((cx + 42, cy - 64, cx + 42, cy + 64), fill=e, width=3)
        draw.polygon([(cx - 8, cy - 20), (cx + 8, cy - 20), (cx + 8, cy + 40), (cx - 8, cy + 40)], outline=g, width=2)
        draw.ellipse((cx - 12, cy - 52, cx + 12, cy - 28), outline=g, width=2)
        draw.line((cx - 32, cy + 8, cx + 32, cy + 40), fill=L, width=3)
        draw.line((cx + 32, cy + 8, cx - 32, cy + 40), fill=L, width=3)
    elif roman == "VI":  # Los Enamorados
        draw.ellipse((cx - 44, cy - 28, cx - 16, cy + 8), outline=g, width=2)
        draw.ellipse((cx + 16, cy - 28, cx + 44, cy + 8), outline=g, width=2)
        draw.line((cx - 30, cy + 8, cx - 30, cy + 52), fill=g, width=3)
        draw.line((cx + 30, cy + 8, cx + 30, cy + 52), fill=g, width=3)
        draw.arc((cx - 20, cy - 70, cx + 20, cy - 30), 200, 340, fill=L, width=2)
        _star_fill(draw, cx, cy - 58, 14, 8, L)
        draw.line((cx - 8, cy + 20, cx + 8, cy + 20), fill=d, width=2)
    elif roman == "VII":  # El Carro
        draw.polygon([(cx - 52, cy + 8), (cx - 34, cy - 36), (cx + 34, cy - 36), (cx + 52, cy + 8)], outline=g, width=2)
        draw.rectangle((cx - 28, cy - 58, cx + 28, cy - 36), outline=L, width=2)
        draw.ellipse((cx - 44, cy + 14, cx - 16, cy + 42), outline=g, width=2)
        draw.ellipse((cx + 16, cy + 14, cx + 44, cy + 42), outline=g, width=2)
        draw.line((cx - 16, cy + 28, cx + 16, cy + 28), fill=d, width=2)
        _star(draw, cx, cy - 48, 8, 4, L)
    elif roman == "VIII":  # La Justicia
        draw.line((cx, cy - 48, cx, cy + 56), fill=g, width=3)
        draw.line((cx - 46, cy - 20, cx + 46, cy - 20), fill=g, width=3)
        draw.ellipse((cx - 54, cy - 40, cx - 26, cy - 12), outline=L, width=2)
        draw.ellipse((cx + 26, cy - 40, cx + 54, cy - 12), outline=L, width=2)
        draw.polygon([(cx - 12, cy + 20), (cx, cy + 60), (cx + 12, cy + 20)], outline=g, width=2)
        draw.rectangle((cx - 8, cy - 64, cx + 8, cy - 48), outline=d, width=1)
    elif roman == "IX":  # El Ermitaño
        draw.polygon([(cx - 8, cy - 20), (cx + 36, cy - 8), (cx - 8, cy + 8)], outline=L, width=2)  # lantern
        draw.ellipse((cx + 18, cy - 18, cx + 34, cy - 2), outline=L, width=2)
        _star_fill(draw, cx + 26, cy - 10, 5, 4, L)
        draw.line((cx - 8, cy + 8, cx - 8, cy + 52), fill=g, width=3)
        draw.arc((cx - 40, cy - 40, cx + 8, cy + 48), 250, 90, fill=g, width=3)  # cloak
        draw.ellipse((cx - 20, cy - 58, cx + 4, cy - 34), outline=g, width=2)
    elif roman == "X":  # La Rueda
        draw.ellipse((cx - 56, cy - 56, cx + 56, cy + 56), outline=g, width=3)
        draw.ellipse((cx - 36, cy - 36, cx + 36, cy + 36), outline=d, width=2)
        draw.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=L)
        for i in range(8):
            ang = i * math.pi / 4
            draw.line((cx, cy, cx + 56 * math.cos(ang), cy + 56 * math.sin(ang)), fill=g, width=2)
        for i, glyph in enumerate(("A",)):
            pass
        draw.polygon([(cx + 40, cy - 64), (cx + 52, cy - 40), (cx + 28, cy - 40)], outline=e, width=1)
        draw.polygon([(cx - 40, cy + 64), (cx - 52, cy + 40), (cx - 28, cy + 40)], outline=e, width=1)
    elif roman == "XI":  # La Fuerza
        draw.ellipse((cx - 20, cy - 64, cx + 20, cy - 28), outline=g, width=2)
        draw.arc((cx - 36, cy - 78, cx + 36, cy - 40), 20, 160, fill=L, width=2)
        draw.arc((cx - 50, cy - 10, cx + 50, cy + 60), 200, 340, fill=g, width=3)  # lion mane
        draw.ellipse((cx - 28, cy + 4, cx + 28, cy + 48), outline=g, width=2)
        draw.arc((cx - 18, cy + 20, cx + 18, cy + 44), 20, 160, fill=L, width=2)  # closed jaws
    elif roman == "XII":  # El Colgado
        draw.line((cx - 48, cy - 58, cx + 48, cy - 58), fill=g, width=3)
        draw.line((cx, cy - 58, cx, cy - 20), fill=g, width=3)
        draw.ellipse((cx - 12, cy + 28, cx + 12, cy + 52), outline=g, width=2)  # head down
        draw.line((cx, cy - 20, cx, cy + 28), fill=g, width=3)
        draw.line((cx, cy - 4, cx - 28, cy + 20), fill=g, width=2)
        draw.line((cx, cy - 4, cx + 28, cy + 20), fill=g, width=2)
        draw.ellipse((cx - 22, cy + 20, cx + 22, cy + 58), outline=L, width=1)  # halo
    elif roman == "XIII":  # La Muerte
        draw.ellipse((cx - 54, cy + 20, cx + 10, cy + 64), outline=d, width=2)  # horse
        draw.line((cx - 8, cy - 40, cx - 8, cy + 28), fill=g, width=3)  # rider
        draw.polygon([(cx - 8, cy - 28), (cx + 48, cy - 16), (cx - 8, cy - 4)], outline=L, width=2)  # banner
        _star(draw, cx + 28, cy - 16, 7, 4, L)
        draw.ellipse((cx - 18, cy - 58, cx + 2, cy - 38), outline=g, width=2)
        draw.arc((cx + 20, cy + 40, cx + 64, cy + 70), 200, 20, fill=e, width=2)  # setting sun
    elif roman == "XIV":  # La Templanza
        draw.ellipse((cx - 12, cy - 64, cx + 12, cy - 40), outline=g, width=2)
        draw.line((cx, cy - 40, cx, cy + 8), fill=g, width=3)
        draw.arc((cx - 50, cy - 8, cx - 8, cy + 40), 200, 20, fill=L, width=3)
        draw.arc((cx + 8, cy - 8, cx + 50, cy + 40), 200, 20, fill=L, width=3)
        draw.line((cx - 28, cy - 4, cx + 28, cy + 12), fill=g, width=2)
        draw.arc((cx - 60, cy + 36, cx + 60, cy + 72), 200, 340, fill=d, width=2)  # river
        draw.line((cx - 16, cy + 8, cx - 28, cy + 52), fill=g, width=2)
        draw.line((cx + 16, cy + 8, cx + 24, cy + 40), fill=g, width=2)
    elif roman == "XV":  # El Diablo
        draw.polygon([(cx - 18, cy - 20), (cx, cy - 64), (cx + 18, cy - 20)], outline=g, width=2)
        draw.line((cx - 22, cy - 64, cx - 8, cy - 40), fill=g, width=2)
        draw.line((cx + 22, cy - 64, cx + 8, cy - 40), fill=g, width=2)
        draw.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), outline=g, width=2)
        draw.line((cx, cy + 20, cx, cy + 40), fill=g, width=3)
        draw.line((cx - 36, cy + 24, cx - 36, cy + 56), fill=d, width=2)
        draw.line((cx + 36, cy + 24, cx + 36, cy + 56), fill=d, width=2)
        draw.arc((cx - 48, cy + 40, cx - 24, cy + 64), 0, 180, fill=d, width=2)
        draw.arc((cx + 24, cy + 40, cx + 48, cy + 64), 0, 180, fill=d, width=2)
        draw.line((cx + 8, cy - 8, cx + 28, cy + 24), fill=L, width=2)  # inverted torch
    elif roman == "XVI":  # La Torre
        draw.rectangle((cx - 28, cy - 8, cx + 28, cy + 64), outline=g, width=3)
        draw.polygon([(cx - 28, cy - 8), (cx, cy - 40), (cx + 28, cy - 8)], outline=L, width=2)
        draw.polygon([(cx - 10, cy - 52), (cx + 10, cy - 52), (cx + 6, cy - 40), (cx - 6, cy - 40)], outline=L, width=1)  # crown
        draw.line((cx - 60, cy - 64, cx + 20, cy - 12), fill=L, width=4)  # lightning
        draw.line((cx - 20, cy - 56, cx - 4, cy - 28), fill=L, width=2)
        for yy in (8, 28, 48):
            draw.rectangle((cx - 12, cy + yy, cx + 12, cy + yy + 10), outline=e, width=1)
        draw.line((cx - 40, cy + 20, cx - 28, cy + 48), fill=d, width=2)
        draw.line((cx + 40, cy + 16, cx + 28, cy + 44), fill=d, width=2)
    elif roman == "XVII":  # La Estrella
        _star_fill(draw, cx, cy - 28, 42, 8, L)
        _star(draw, cx, cy - 28, 42, 8, g, 2)
        draw.ellipse((cx - 8, cy - 36, cx + 8, cy - 20), fill=g)
        draw.arc((cx - 40, cy + 16, cx + 8, cy + 56), 200, 20, fill=g, width=2)
        draw.arc((cx - 8, cy + 24, cx + 40, cy + 64), 200, 20, fill=g, width=2)
        draw.line((cx - 48, cy + 48, cx + 48, cy + 48), fill=d, width=1)
        for i in range(7):
            ang = i * math.pi / 3.5
            _star(draw, int(cx + 70 * math.cos(ang)), int(cy - 10 + 58 * math.sin(ang)), 5, 4, d)
    elif roman == "XVIII":  # La Luna
        draw.arc((cx - 40, cy - 50, cx + 36, cy + 36), 40, 280, fill=L, width=4)
        draw.ellipse((cx + 8, cy - 12, cx + 24, cy + 4), outline=g, width=1)
        draw.line((cx - 56, cy - 40, cx - 56, cy + 56), fill=e, width=3)
        draw.line((cx + 56, cy - 40, cx + 56, cy + 56), fill=e, width=3)
        draw.ellipse((cx - 14, cy + 36, cx + 14, cy + 58), outline=g, width=2)  # crayfish
        draw.polygon([(cx - 36, cy + 28), (cx - 20, cy + 8), (cx - 12, cy + 28)], outline=d, width=1)
        draw.polygon([(cx + 36, cy + 28), (cx + 20, cy + 8), (cx + 12, cy + 28)], outline=d, width=1)
        draw.line((cx, cy + 20, cx, cy + 64), fill=d, width=1)
    elif roman == "XIX":  # El Sol
        draw.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), outline=g, width=3)
        draw.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=L)
        for i in range(16):
            ang = i * math.pi / 8
            r0, r1 = (40, 62) if i % 2 == 0 else (38, 52)
            draw.line(
                (cx + r0 * math.cos(ang), cy + r0 * math.sin(ang), cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)),
                fill=g,
                width=2,
            )
        draw.ellipse((cx - 10, cy + 40, cx + 10, cy + 58), outline=d, width=1)
        draw.line((cx, cy + 58, cx, cy + 70), fill=d, width=1)
    elif roman == "XX":  # El Juicio
        draw.ellipse((cx - 20, cy - 70, cx + 20, cy - 34), outline=g, width=2)
        draw.polygon([(cx - 6, cy - 34), (cx + 6, cy - 34), (cx + 6, cy + 4), (cx + 40, cy + 16), (cx - 6, cy + 4)], outline=L, width=2)
        draw.arc((cx - 54, cy + 8, cx + 54, cy + 64), 200, 340, fill=g, width=3)
        for ox in (-28, 0, 28):
            draw.ellipse((cx + ox - 8, cy + 36, cx + ox + 8, cy + 56), outline=d, width=1)
            draw.line((cx + ox, cy + 56, cx + ox, cy + 68), fill=d, width=1)
    else:  # XXI El Mundo
        draw.ellipse((cx - 58, cy - 48, cx + 58, cy + 56), outline=g, width=3)
        draw.ellipse((cx - 20, cy - 20, cx + 20, cy + 24), outline=L, width=2)
        _star_fill(draw, cx, cy, 8, 4, L)
        for ang, rr in ((-0.8, 78), (0.8, 78), (math.pi - 0.8, 78), (math.pi + 0.8, 78)):
            ex = int(cx + rr * math.cos(ang))
            ey = int(cy + 4 + rr * 0.7 * math.sin(ang))
            draw.ellipse((ex - 10, ey - 10, ex + 10, ey + 10), outline=e, width=1)


def _draw_frames(draw: ImageDraw.ImageDraw, width: int, height: int, p: dict[str, tuple[int, int, int]]) -> None:
    # Layered museum naipe frames: outer bevel, gold leaf, lit hairline, mat, parchment plate.
    draw.rounded_rectangle((18, 18, width - 18, height - 18), radius=40, outline=p["shadow"], width=6)
    draw.rounded_rectangle((26, 26, width - 26, height - 26), radius=36, fill=p["card"], outline=p["gold"], width=11)
    draw.rounded_rectangle((38, 38, width - 38, height - 38), radius=30, outline=p["gold_lit"], width=2)
    draw.rounded_rectangle((46, 46, width - 46, height - 46), radius=28, fill=p["mat"], outline=p["gold_dim"], width=1)
    draw.rounded_rectangle((58, 58, width - 58, height - 58), radius=24, outline=p["edge"], width=1)
    draw.rounded_rectangle((68, 68, width - 68, height - 68), radius=20, outline=p["gold"], width=2)
    draw.rounded_rectangle((78, 78, width - 78, height - 78), radius=16, fill=p["parchment"], outline=p["gold_dim"], width=1)
    # Inner luminous plate
    draw.rounded_rectangle((90, 90, width - 90, height - 90), radius=12, outline=p["gold_lit"], width=1)

    _filigree_corner(draw, 96, 96, 1, 1, p["gold"], p["gold_lit"], p["gold_dim"])
    _filigree_corner(draw, width - 96, 96, -1, 1, p["gold"], p["gold_lit"], p["gold_dim"])
    _filigree_corner(draw, 96, height - 96, 1, -1, p["gold"], p["gold_lit"], p["gold_dim"])
    _filigree_corner(draw, width - 96, height - 96, -1, -1, p["gold"], p["gold_lit"], p["gold_dim"])
    _side_flourish(draw, 104, 220, height - 220, p["gold"], p["gold_lit"], left=True)
    _side_flourish(draw, width - 104, 220, height - 220, p["gold"], p["gold_lit"], left=False)


def render_spread(spread: Spread) -> bytes:
    palette = PALETTES.get(spread.avatar_id, PALETTES["arcana"])
    width, height = 768, 1280
    card = spread.cards[0]
    seed = int(hashlib.sha256(f"{spread.avatar_id}|{card.roman}|{card.name}".encode("utf-8")).hexdigest()[:8], 16)

    base = _vertical_gradient((width, height), palette["bg"], palette["velvet"])
    light = _soft_light((width, height), palette)
    image = Image.blend(base, light, 0.55)

    draw = ImageDraw.Draw(image)
    _draw_frames(draw, width, height, palette)
    # Inner luminous plate + quiet medallion wash (no expensive full-frame blur)
    draw.rounded_rectangle((100, 100, width - 100, height - 100), radius=14, fill=palette["parchment_lit"])
    draw.ellipse((width // 2 - 118, 312, width // 2 + 118, 548), fill=palette["parchment"])
    draw.ellipse((width // 2 - 100, 330, width // 2 + 100, 530), outline=palette["gold_dim"], width=1)

    title_font = _font(20, bold=True)
    card_title = _font(40, bold=True)
    roman_font = _font(76, bold=True)
    body_font = _font(21)
    small_font = _font(14)
    italic_guess = _font(19)
    house = "ARCANA" if spread.avatar_id == "arcana" else "ARCANO"

    _center_shadow(draw, 112, house, title_font, palette["gold_lit"], palette["shadow"], width)
    _center(draw, 142, "UN ARCANO MAYOR", small_font, palette["mute"], width)
    _ornament_rule(draw, 178, width, palette["gold"], palette["gold_lit"], palette["gold_dim"])

    _center_shadow(draw, 200, card.roman, roman_font, palette["gold_lit"], palette["ink"], width, dx=2, dy=3)
    _emblem(
        draw,
        card.roman,
        width // 2,
        430,
        palette["gold"],
        palette["gold_lit"],
        palette["edge"],
        palette["gold_dim"],
    )
    _ornament_rule(draw, 568, width, palette["gold"], palette["gold_lit"], palette["gold_dim"])
    _center_shadow(draw, 586, card.name, card_title, palette["text"], palette["ink"], width, dx=2, dy=2)

    keywords = "  ·  ".join(part.strip() for part in card.keywords.split(",") if part.strip())
    _center(draw, 644, keywords, body_font, palette["mute"], width)

    draw.rounded_rectangle((120, height - 292, width - 120, height - 118), radius=14, outline=palette["gold_dim"], width=1)
    draw.line((int(width * 0.30), height - 268, int(width * 0.70), height - 268), fill=palette["edge"], width=1)
    _center(draw, height - 258, "la consulta", small_font, palette["mute"], width)
    y = height - 224
    for line in _wrap(draw, spread.question, italic_guess, width - 260)[:4]:
        _center(draw, y, line, italic_guess, palette["text"], width)
        y += 30

    image = _apply_grain(image, seed=seed, amount=0.055)

    # Crisp final frame hairlines after grain
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((26, 26, width - 26, height - 26), radius=36, outline=palette["gold"], width=2)
    draw.rounded_rectangle((38, 38, width - 38, height - 38), radius=30, outline=palette["gold_lit"], width=1)

    buffer = BytesIO()
    image.save(buffer, format="PNG", compress_level=5)
    return buffer.getvalue()
