from app.services.tarot import draw_spread, render_spread


def test_same_question_same_cards():
    first = draw_spread("cambio de trabajo", "arcana")
    second = draw_spread("cambio de trabajo", "arcana")
    assert [c.name for c in first.cards] == [c.name for c in second.cards]


def test_briefing_contains_question_and_three_cards():
    spread = draw_spread("¿me mudo de ciudad?", "arcano")
    text = spread.briefing()
    assert "¿me mudo de ciudad?" in text
    assert "Pasado" in text and "Presente" in text and "Futuro" in text
    assert text.count("- ") == 3


def test_render_png_header():
    spread = draw_spread("amor", "arcana")
    png = render_spread(spread)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert len(png) > 1000
