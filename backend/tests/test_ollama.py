from app.adapters.llm.ollama import NUM_CTX, NUM_PREDICT


def test_ollama_room_for_readings():
    assert NUM_PREDICT >= 480
    assert NUM_CTX >= 2048
