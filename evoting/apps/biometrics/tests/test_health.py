"""Health endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_ok_without_auth(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["embedder"] == "hash-v1"


def test_health_echoes_request_id(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "abc-123"})
    assert response.headers["X-Request-ID"] == "abc-123"
