"""Verification (challenge + match) endpoint tests."""

from __future__ import annotations

import base64

from fastapi.testclient import TestClient

from app.liveness import CHALLENGES

ENROLLED_IMAGE = b"\x89PNG\r\n" + b"enrolled-voter-face-image-" * 20
DIFFERENT_IMAGE = b"\x89PNG\r\n" + b"a-completely-different-face-" * 20
FRAME_A = b"\x89PNG\r\n" + b"liveness-frame-one-" * 20
FRAME_B = b"\x89PNG\r\n" + b"liveness-frame-two-" * 20


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def _embed(client: TestClient, headers: dict[str, str], image: bytes) -> list[float]:
    response = client.post("/enrollment/embed", json={"image_b64": _b64(image)}, headers=headers)
    assert response.status_code == 200
    embedding: list[float] = response.json()["embedding"]
    return embedding


def test_challenge_returns_valid_value(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post("/verification/challenge", json={}, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["challenge"] in CHALLENGES
    assert isinstance(body["challenge_id"], str) and body["challenge_id"]


def test_match_success_with_identical_embedding(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    stored = _embed(client, auth_headers, ENROLLED_IMAGE)
    payload = {
        "probe_image_b64": _b64(ENROLLED_IMAGE),
        "frames_b64": [_b64(FRAME_A), _b64(FRAME_B)],
        "challenge": "blink",
        "stored_embedding": stored,
        "threshold": 0.42,
    }
    response = client.post("/verification/match", json=payload, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["passed"] is True
    assert body["liveness_passed"] is True
    assert body["face_score"] > 0.99
    assert body["reason"] == "ok"


def test_match_fails_for_different_face(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    stored = _embed(client, auth_headers, ENROLLED_IMAGE)
    payload = {
        "probe_image_b64": _b64(DIFFERENT_IMAGE),
        "frames_b64": [_b64(FRAME_A), _b64(FRAME_B)],
        "challenge": "blink",
        "stored_embedding": stored,
        "threshold": 0.42,
    }
    response = client.post("/verification/match", json=payload, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["passed"] is False
    assert body["liveness_passed"] is True
    assert body["face_score"] < 0.42
    assert body["reason"] == "face_mismatch"


def test_match_fails_liveness_with_single_frame(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    stored = _embed(client, auth_headers, ENROLLED_IMAGE)
    payload = {
        "probe_image_b64": _b64(ENROLLED_IMAGE),
        "frames_b64": [_b64(FRAME_A)],
        "challenge": "blink",
        "stored_embedding": stored,
        "threshold": 0.42,
    }
    response = client.post("/verification/match", json=payload, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["passed"] is False
    assert body["liveness_passed"] is False
    assert body["reason"] == "liveness_failed"


def test_match_uses_last_frame_when_probe_null(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    stored = _embed(client, auth_headers, FRAME_B)
    payload = {
        "probe_image_b64": None,
        "frames_b64": [_b64(FRAME_A), _b64(FRAME_B)],
        "challenge": "smile",
        "stored_embedding": stored,
        "threshold": 0.42,
    }
    response = client.post("/verification/match", json=payload, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["passed"] is True
    assert body["face_score"] > 0.99
