from app.domain.intent import wants_spread


def test_hola_does_not_draw():
    assert wants_spread("hola") is False
    assert wants_spread("Hola!") is False
    assert wants_spread("buenas tardes") is False


def test_explicit_flag_always_draws():
    assert wants_spread("hola", explicit=True) is True


def test_asks_for_reading():
    assert wants_spread("Sí, lanza una tirada de tres cartas") is True
    assert wants_spread("hazme una lectura") is True
    assert wants_spread("tira las cartas") is True
