from app.domain.models import ChatMessage
from app.services.conversations import ConversationStore


def test_sqlite_roundtrip(tmp_path):
    store = ConversationStore(tmp_path / "c.db")
    conv = store.create("enigma")
    store.append(conv.id, ChatMessage(role="user", content="hola"))
    store.append(conv.id, ChatMessage(role="assistant", content="saludos"))
    loaded = store.get(conv.id)
    assert loaded.avatar_id == "enigma"
    assert [m.content for m in loaded.messages] == ["hola", "saludos"]
    listed = store.list_for_avatar("enigma")
    assert listed[0].id == conv.id


def test_conversation_api(client):
    store = client.app.state.conversations
    conv = store.create("arcana")
    store.append(conv.id, ChatMessage(role="user", content="cartas"))
    response = client.get(f"/api/conversations/{conv.id}")
    assert response.status_code == 200
    assert response.json()["avatar_id"] == "arcana"
    listed = client.get("/api/avatars/arcana/conversations")
    assert listed.status_code == 200
    assert listed.json()["conversations"][0]["message_count"] == 1
