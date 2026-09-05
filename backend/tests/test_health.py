def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "enigma" in body["avatars"]
    assert "providers" in body
    assert "ollama" in body["providers"]
    assert "spacexai" in body["providers"]
    assert "api_key_present" in body["providers"]["spacexai"]
    # Never leak the key value.
    flat = str(body)
    assert "xai-" not in flat.lower() or body["providers"]["spacexai"]["api_key_present"] in (True, False)
    assert "api_key" not in body["providers"]["spacexai"] or "api_key_present" in body["providers"]["spacexai"]
