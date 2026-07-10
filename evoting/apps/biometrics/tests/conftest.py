"""Shared pytest fixtures."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings

TEST_TOKEN = "test-internal-token-123"
AUTH_HEADERS = {"X-Internal-Token": TEST_TOKEN}


@pytest.fixture(autouse=True)
def _configure_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Set a known internal token and hash embedder, clearing cached settings."""
    monkeypatch.setenv("INTERNAL_SERVICE_TOKEN", TEST_TOKEN)
    monkeypatch.setenv("FACE_EMBEDDER", "hash")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> Iterator[TestClient]:
    """A TestClient bound to a freshly created app."""
    # Imported here so the env fixture applies before the app reads settings.
    from app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return dict(AUTH_HEADERS)
