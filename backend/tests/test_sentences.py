from app.domain.sentences import split_ready_sentences


def test_split_two_sentences():
    ready, rest = split_ready_sentences("Hola mundo. ¿Seguimos?")
    assert ready == ["Hola mundo.", "¿Seguimos?"]
    assert rest == ""


def test_keeps_incomplete_tail():
    ready, rest = split_ready_sentences("Primera frase. Segunda incompleta")
    assert ready == ["Primera frase."]
    assert rest == "Segunda incompleta"


def test_empty():
    ready, rest = split_ready_sentences("")
    assert ready == []
    assert rest == ""


def test_ellipsis_and_exclaim():
    ready, rest = split_ready_sentences("Cuidado… Sigue. ")
    assert "Cuidado…" in ready[0] or ready[0].startswith("Cuidado")
    assert rest == ""


def test_splits_newline_thought():
    ready, rest = split_ready_sentences("Primera idea" + chr(10) + "Segunda idea. ")
    assert ready[0] == "Primera idea"
    assert any("Segunda idea." in item for item in ready)
    assert rest == ""
