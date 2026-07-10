"""End-to-end voter journey and the security invariants that protect it."""

from __future__ import annotations

import base64
from datetime import UTC, datetime, timedelta

from httpx import AsyncClient

ENROLL_IMAGE = b"a-real-enough-face-image-payload" * 8  # > 100 bytes
FRAME_A = base64.b64encode(b"frame-one" * 20).decode()
FRAME_B = base64.b64encode(b"frame-two-different" * 20).decode()
PROBE = base64.b64encode(ENROLL_IMAGE).decode()  # matches the enrolled template


async def _assembly_id(client: AsyncClient, code: str = "MH-AC-003") -> str:
    states = (await client.get("/geo/states")).json()
    mh = next(s for s in states if s["code"] == "MH")
    districts = (await client.get(f"/geo/states/{mh['id']}/districts")).json()
    d = next(d for d in districts if d["code"] == "MH-D-02")
    assemblies = (await client.get(f"/geo/districts/{d['id']}/assemblies")).json()
    return str(next(a for a in assemblies if a["code"] == code)["id"])


async def _register_voter(client: AsyncClient, ac_id: str, *, email: str, aadhaar: str) -> dict:
    resp = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": "Test Voter",
            "dob": "1990-01-01",
            "gender": "male",
            "aadhaar": aadhaar,
            "assembly_constituency_id": ac_id,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def _login(client: AsyncClient, email: str) -> str:
    resp = await client.post("/auth/login", json={"email": email, "password": "password123"})
    assert resp.status_code == 200, resp.text
    return str(resp.json()["access_token"])


async def _create_election(client: AsyncClient, admin_token: str, ac_id: str) -> dict:
    now = datetime.now(UTC)
    resp = await client.post(
        "/admin/elections",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Mumbai North Assembly 2026",
            "election_type": "assembly",
            "assembly_constituency_id": ac_id,
            "start_at": (now - timedelta(minutes=1)).isoformat(),
            "end_at": (now + timedelta(hours=2)).isoformat(),
            "candidates": [
                {"name": "Candidate A", "party": "Party X"},
                {"name": "Candidate B", "party": "Party Y"},
            ],
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def _verify(client: AsyncClient, token: str, election_id: str) -> str:
    auth = {"Authorization": f"Bearer {token}"}
    start = await client.post(
        "/verification/start", params={"election_id": election_id}, headers=auth
    )
    assert start.status_code == 200, start.text
    body = start.json()
    face = await client.post(
        "/verification/face",
        headers=auth,
        json={
            "request_id": body["request_id"],
            "election_id": election_id,
            "challenge": body["challenge"],
            "frames_b64": [FRAME_A, FRAME_B],
            "probe_image_b64": PROBE,
        },
    )
    assert face.status_code == 200, face.text
    assert face.json()["passed"] is True
    return str(body["request_id"])


async def test_full_vote_flow(client: AsyncClient, admin_token: str) -> None:
    ac_id = await _assembly_id(client)
    voter = await _register_voter(client, ac_id, email="voter1@test.com", aadhaar="111122223333")

    # Admin approves the voter.
    approve = await client.patch(
        f"/admin/voters/{voter['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "accepted"},
    )
    assert approve.status_code == 200, approve.text

    token = await _login(client, "voter1@test.com")
    auth = {"Authorization": f"Bearer {token}"}

    # Enroll face.
    enroll = await client.post(
        "/enrollment/face", headers=auth, files={"file": ("face.jpg", ENROLL_IMAGE, "image/jpeg")}
    )
    assert enroll.status_code == 200, enroll.text
    assert enroll.json()["enrolled"] is True

    election = await _create_election(client, admin_token, ac_id)
    election_id = election["id"]

    # Active elections for the voter's constituency.
    elections = (await client.get("/voting/elections", headers=auth)).json()
    assert any(e["id"] == election_id for e in elections)

    candidates = (
        await client.get(f"/voting/elections/{election_id}/candidates", headers=auth)
    ).json()
    assert len(candidates) == 2

    request_id = await _verify(client, token, election_id)

    # Cast vote.
    cast = await client.post(
        "/voting/cast",
        headers=auth,
        json={
            "election_id": election_id,
            "candidate_id": candidates[0]["id"],
            "verification_request_id": request_id,
        },
    )
    assert cast.status_code == 201, cast.text
    receipt = cast.json()
    assert receipt["tx_hash"].startswith("0x")

    # Results (admin) reflect the single vote from chain.
    results = (
        await client.get(
            f"/admin/elections/{election_id}/results",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    ).json()
    assert results["total_votes"] == 1
    winner = results["results"][0]
    assert winner["votes"] == 1


async def test_double_vote_rejected(client: AsyncClient, admin_token: str) -> None:
    ac_id = await _assembly_id(client)
    voter = await _register_voter(client, ac_id, email="voter2@test.com", aadhaar="222233334444")
    await client.patch(
        f"/admin/voters/{voter['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "accepted"},
    )
    token = await _login(client, "voter2@test.com")
    auth = {"Authorization": f"Bearer {token}"}
    await client.post(
        "/enrollment/face", headers=auth, files={"file": ("f.jpg", ENROLL_IMAGE, "image/jpeg")}
    )
    election = await _create_election(client, admin_token, ac_id)
    eid = election["id"]
    candidates = (
        await client.get(f"/voting/elections/{eid}/candidates", headers=auth)
    ).json()

    rid1 = await _verify(client, token, eid)
    first = await client.post(
        "/voting/cast",
        headers=auth,
        json={
            "election_id": eid,
            "candidate_id": candidates[0]["id"],
            "verification_request_id": rid1,
        },
    )
    assert first.status_code == 201

    # Fresh verification, second vote attempt -> 409 already voted.
    rid2 = await _verify(client, token, eid)
    second = await client.post(
        "/voting/cast",
        headers=auth,
        json={
            "election_id": eid,
            "candidate_id": candidates[1]["id"],
            "verification_request_id": rid2,
        },
    )
    assert second.status_code == 409, second.text
    assert second.json()["code"] == "ALREADY_VOTED"


async def test_vote_requires_verification(client: AsyncClient, admin_token: str) -> None:
    ac_id = await _assembly_id(client)
    voter = await _register_voter(client, ac_id, email="voter3@test.com", aadhaar="333344445555")
    await client.patch(
        f"/admin/voters/{voter['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "accepted"},
    )
    token = await _login(client, "voter3@test.com")
    auth = {"Authorization": f"Bearer {token}"}
    await client.post(
        "/enrollment/face", headers=auth, files={"file": ("f.jpg", ENROLL_IMAGE, "image/jpeg")}
    )
    election = await _create_election(client, admin_token, ac_id)
    eid = election["id"]
    candidates = (
        await client.get(f"/voting/elections/{eid}/candidates", headers=auth)
    ).json()

    import uuid

    resp = await client.post(
        "/voting/cast",
        headers=auth,
        json={
            "election_id": eid,
            "candidate_id": candidates[0]["id"],
            "verification_request_id": str(uuid.uuid4()),
        },
    )
    assert resp.status_code == 422
    assert resp.json()["code"] == "VERIFICATION_MISSING"


async def test_unapproved_voter_cannot_vote(client: AsyncClient, admin_token: str) -> None:
    ac_id = await _assembly_id(client)
    await _register_voter(client, ac_id, email="voter4@test.com", aadhaar="444455556666")
    token = await _login(client, "voter4@test.com")
    auth = {"Authorization": f"Bearer {token}"}
    await client.post(
        "/enrollment/face", headers=auth, files={"file": ("f.jpg", ENROLL_IMAGE, "image/jpeg")}
    )
    election = await _create_election(client, admin_token, ac_id)
    eid = election["id"]
    candidates = (
        await client.get(f"/voting/elections/{eid}/candidates", headers=auth)
    ).json()
    rid = await _verify(client, token, eid)
    resp = await client.post(
        "/voting/cast",
        headers=auth,
        json={
            "election_id": eid,
            "candidate_id": candidates[0]["id"],
            "verification_request_id": rid,
        },
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "NOT_APPROVED"


async def test_duplicate_aadhaar_rejected(client: AsyncClient) -> None:
    ac_id = await _assembly_id(client)
    await _register_voter(client, ac_id, email="a@test.com", aadhaar="777788889999")
    resp = await client.post(
        "/auth/register",
        json={
            "email": "b@test.com",
            "password": "password123",
            "full_name": "Dup Aadhaar",
            "dob": "1990-01-01",
            "gender": "female",
            "aadhaar": "777788889999",
            "assembly_constituency_id": ac_id,
        },
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "AADHAAR_TAKEN"
