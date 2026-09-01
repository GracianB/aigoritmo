import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.domain.models import ChatMessage, Conversation


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConversationStore:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    avatar_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);
                CREATE INDEX IF NOT EXISTS idx_conv_avatar ON conversations(avatar_id);
                """
            )

    def create(self, avatar_id: str) -> Conversation:
        conv = Conversation(id=str(uuid.uuid4()), avatar_id=avatar_id, messages=[])
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO conversations (id, avatar_id, created_at) VALUES (?, ?, ?)",
                (conv.id, conv.avatar_id, _utc_now()),
            )
        return conv

    def get(self, conversation_id: str) -> Conversation:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, avatar_id FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()
            if row is None:
                raise KeyError(f"unknown conversation: {conversation_id}")
            messages = [
                ChatMessage(role=m["role"], content=m["content"])
                for m in conn.execute(
                    "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id",
                    (conversation_id,),
                ).fetchall()
            ]
        return Conversation(id=row["id"], avatar_id=row["avatar_id"], messages=messages)

    def append(self, conversation_id: str, message: ChatMessage) -> Conversation:
        with self._connect() as conn:
            exists = conn.execute(
                "SELECT 1 FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()
            if exists is None:
                raise KeyError(f"unknown conversation: {conversation_id}")
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (conversation_id, message.role, message.content, _utc_now()),
            )
        return self.get(conversation_id)

    def list_for_avatar(self, avatar_id: str, limit: int = 20) -> list[Conversation]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id FROM conversations WHERE avatar_id = ? ORDER BY created_at DESC LIMIT ?",
                (avatar_id, limit),
            ).fetchall()
        return [self.get(row["id"]) for row in rows]
