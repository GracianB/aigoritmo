from app.domain.avatars import AvatarCatalog
from app.core.config import PROJECT_DIR


EXPECTED = 20


def test_list_avatars(client):
    response = client.get("/api/avatars")
    assert response.status_code == 200
    ids = [item["id"] for item in response.json()["avatars"]]
    assert len(ids) == EXPECTED
    assert ids == sorted(ids)
    assert "enigma" in ids
    assert "bauri" in ids
    assert "qwen" in ids


def test_get_enigma(client):
    response = client.get("/api/avatars/enigma")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Enigma"
    assert body["voice"]["voice_id"] == "es-odal-medium"


def test_unknown_avatar(client):
    response = client.get("/api/avatars/nope")
    assert response.status_code == 404


def test_invalid_yaml_fails_fast(tmp_path):
    bad = tmp_path / "broken.yaml"
    bad.write_text("id: x\n", encoding="utf-8")
    try:
        AvatarCatalog(tmp_path)
        raise AssertionError("expected validation error")
    except Exception:
        pass


def test_catalog_loads_real_avatars():
    catalog = AvatarCatalog(PROJECT_DIR / "avatars")
    assert len(catalog.list()) == EXPECTED
    enigma = catalog.get("enigma")
    assert enigma.llm.provider == "ollama"
    for avatar in catalog.list():
        assert avatar.poster.startswith("/media/image/")
        assert avatar.voice.provider == "piper"
        assert avatar.system_prompt.strip()


def test_arcana_uses_feminine_high_voice():
    catalog = AvatarCatalog(PROJECT_DIR / "avatars")
    voice = catalog.get("arcana").voice
    assert voice.voice_id == "es_AR-daniela-high"
    assert voice.fallback_voice_id == "es_MX-laura-high"
    assert voice.length_scale >= 1.0
