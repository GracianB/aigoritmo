from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    get_settings.cache_clear()
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
    get_settings.cache_clear()
