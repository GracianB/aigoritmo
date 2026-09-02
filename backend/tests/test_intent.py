from app.domain.intent import wants_spread


def test_hola_does_not_draw():
    assert wants_spread("hola") is False
    assert wants_spread("Hola!") is False
    assert wants_spread("buenas tardes") is False
    assert wants_spread("Buenos días") is False
    assert wants_spread("qué tal") is False


def test_small_talk_does_not_draw():
    assert wants_spread("cuéntame de ti") is False
    assert wants_spread("quién eres") is False


def test_explicit_flag_always_draws():
    assert wants_spread("hola", explicit=True) is True


def test_asks_for_reading():
    assert wants_spread("Sí, lanza una tirada de una carta") is True
    assert wants_spread("hazme una lectura") is True
    assert wants_spread("tira las cartas") is True
    assert wants_spread("quiero una lectura") is True
    assert wants_spread("una carta sobre el amor") is True