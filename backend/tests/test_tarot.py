from app.adapters.images.pollinations import scene_prompt
from app.services.tarot import draw_spread, render_spread


def test_same_question_same_cards():
    first = draw_spread("cambio de trabajo", "arcana")
    second = draw_spread("cambio de trabajo", "arcana")
    assert [c.name for c in first.cards] == [c.name for c in second.cards]


def test_briefing_contains_question_and_one_card():
    spread = draw_spread("¿me mudo de ciudad?", "arcano")
    text = spread.briefing()
    assert "¿me mudo de ciudad?" in text
    assert len(spread.cards) == 1
    assert text.count("- ") == 1
    assert "Pasado:" not in text and "Presente:" not in text and "Futuro:" not in text
    assert "UN solo arcano" in text


def test_scene_prompt_is_one_tarot_card():
    spread = draw_spread("amor", "arcana")
    prompt = scene_prompt(spread)
    assert "tarot-card shape" in prompt
    assert "one card only" in prompt
    assert "three" not in prompt
    assert spread.cards[0].name in prompt


def test_render_png_header():
    spread = draw_spread("amor", "arcana")
    png = render_spread(spread)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert len(png) > 1000
