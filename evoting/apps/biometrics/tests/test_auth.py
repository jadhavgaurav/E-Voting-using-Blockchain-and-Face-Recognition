"""Internal-token authentication tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_challenge_requires_token(client: TestClient) -> None:
    response = client.post("/verification/challenge", json={})
    assert response.status_code == 401


def test_challenge_rejects_wrong_token(client: TestClient) -> None:
    response = client.post(
        "/verification/challenge",
        json={},
        headers={"X-Internal-Token": "wrong-token"},
    )
    assert response.status_code == 401


def test_challenge_accepts_correct_token(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post("/verification/challenge", json={}, headers=auth_headers)
    assert response.status_code == 200
