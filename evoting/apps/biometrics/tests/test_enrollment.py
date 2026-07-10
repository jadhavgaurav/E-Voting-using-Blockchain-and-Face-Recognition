"""Enrollment (embed) endpoint tests."""

from __future__ import annotations

import base64
import math

from fastapi.testclient import TestClient

VALID_IMAGE = b"\x89PNG\r\n" + b"biometric-test-image-bytes-" * 20


def _l2_norm(vector: list[float]) -> float:
    return math.sqrt(sum(component * component for component in vector))


def test_embed_json_returns_normalized_128_vector(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    image_b64 = base64.b64encode(VALID_IMAGE).decode()
    response = client.post(
        "/enrollment/embed", json={"image_b64": image_b64}, headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["algorithm_version"] == "hash-v1"
    assert len(body["embedding"]) == 128
    assert math.isclose(_l2_norm(body["embedding"]), 1.0, rel_tol=1e-9, abs_tol=1e-9)


def test_embed_multipart_upload(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/enrollment/embed",
        files={"file": ("face.png", VALID_IMAGE, "image/png")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["embedding"]) == 128


def test_embed_tiny_image_returns_no_face(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    image_b64 = base64.b64encode(b"tiny").decode()
    response = client.post(
        "/enrollment/embed", json={"image_b64": image_b64}, headers=auth_headers
    )
    assert response.status_code == 422
    assert response.json()["code"] == "NO_FACE_DETECTED"


def test_embed_empty_image_returns_no_face(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    image_b64 = base64.b64encode(b"").decode()
    response = client.post(
        "/enrollment/embed", json={"image_b64": image_b64}, headers=auth_headers
    )
    assert response.status_code == 422
    assert response.json()["code"] == "NO_FACE_DETECTED"
