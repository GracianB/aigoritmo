from app.domain.speech import prepare_for_speech


def test_strips_markdown_and_urls():
    spoken = prepare_for_speech("**La Torre** avisa. Mira https://example.com ahora.")
    assert "asterisco" not in spoken.lower()
    assert "**" not in spoken
    assert "http" not in spoken
    assert "La Torre" in spoken


def test_skips_empty_and_symbols():
    assert prepare_for_speech("  ***  ") == ""
    assert prepare_for_speech("") == ""


def test_keeps_spanish_punctuation():
    spoken = prepare_for_speech("¿Qué debo soltar? ¡Mira el presente!")
    assert spoken.startswith("¿Qué")
    assert "¡Mira" in spoken
