from app.domain.sentences import split_ready_sentences, take_speakable


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


def test_holds_short_clauses():
    speakable, held = take_speakable("", ["Nombra la carta.", "Di lo que se ve."])
    assert speakable == []
    assert "Nombra la carta." in held
    assert "Di lo que se ve." in held


def test_flushes_long_enough_or_question():
    first, held = take_speakable("", ["Nombra la carta."])
    assert first == []
    speakable, held = take_speakable(held, ["¿Qué te pide hoy esta pausa?"])
    assert any("pide hoy" in item for item in speakable)
    assert held == ""


def test_splits_when_max_chars_exceeded():
    long_a = "Esta frase es lo bastante larga para no mezclarse con la siguiente idea que llega después."
    long_b = "Y esta otra también ocupa un espacio amplio para forzar el corte del acumulador de voz."
    speakable, held = take_speakable("", [long_a, long_b])
    assert long_a in speakable
    assert held == long_b or long_b in speakable
