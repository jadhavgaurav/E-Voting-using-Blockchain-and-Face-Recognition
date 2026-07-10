"""Hardening checks: auth is required, and liveness failure blocks verification."""

from __future__ import annotations

import base64

from httpx import AsyncClient


async def test_protected_endpoints_require_auth(client: AsyncClient) -> None:
    for method, path in [
        ("get", "/auth/me"),
        ("get", "/voting/elections"),
        ("get", "/enrollment/status"),
        ("get", "/admin/elections"),
    ]:
        resp = await client.request(method, path)
        assert resp.status_code == 401, f"{path} -> {resp.status_code}"
        assert resp.json()["code"] in {"UNAUTHORIZED", "FORBIDDEN"}


async def test_bad_token_rejected(client: AsyncClient) -> None:
    resp = await client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401


async def _register_enroll(client: AsyncClient) -> tuple[str, str]:
    states = (await client.get("/geo/states")).json()
    mh = next(s for s in states if s["code"] == "MH")
    districts = (await client.get(f"/geo/states/{mh['id']}/districts")).json()
    d = districts[0]
    assemblies = (await client.get(f"/geo/districts/{d['id']}/assemblies")).json()
    ac_id = str(assemblies[0]["id"])
    await client.post(
        "/auth/register",
        json={
            "email": "live@test.com",
            "password": "password123",
            "full_name": "Live Test",
            "dob": "1990-01-01",
            "gender": "male",
            "aadhaar": "909090909090",
            "assembly_constituency_id": ac_id,
        },
    )
    token = (
        await client.post("/auth/login", json={"email": "live@test.com", "password": "password123"})
    ).json()["access_token"]
    auth = {"Authorization": f"Bearer {token}"}
    await client.post(
        "/enrollment/face",
        headers=auth,
        files={"file": ("f.jpg", b"enrollment-image-payload" * 8, "image/jpeg")},
    )
    return token, ac_id


async def test_liveness_failure_blocks_verification(client: AsyncClient) -> None:
    token, _ = await _register_enroll(client)
    auth = {"Authorization": f"Bearer {token}"}
    start = (await client.post("/verification/start", headers=auth)).json()
    # Only ONE frame -> liveness cannot detect motion -> fail closed.
    single_frame = base64.b64encode(b"only-one-frame").decode()
    resp = await client.post(
        "/verification/face",
        headers=auth,
        json={
            "request_id": start["request_id"],
            "challenge": start["challenge"],
            "frames_b64": [single_frame],
            "probe_image_b64": single_frame,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["passed"] is False
    assert body["liveness_passed"] is False
    assert body["reason"] == "liveness_failed"
