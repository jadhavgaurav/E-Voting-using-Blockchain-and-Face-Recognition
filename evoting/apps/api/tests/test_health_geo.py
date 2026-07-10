"""Health and cascading geography endpoints."""

from __future__ import annotations

from httpx import AsyncClient


async def test_health(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_geo_cascade(client: AsyncClient) -> None:
    states = (await client.get("/geo/states")).json()
    assert {s["code"] for s in states} >= {"MH", "KA", "DL"}

    mh = next(s for s in states if s["code"] == "MH")
    districts = (await client.get(f"/geo/states/{mh['id']}/districts")).json()
    assert len(districts) == 3

    d = next(d for d in districts if d["code"] == "MH-D-02")
    assemblies = (await client.get(f"/geo/districts/{d['id']}/assemblies")).json()
    codes = {a["code"] for a in assemblies}
    assert codes == {"MH-AC-003", "MH-AC-004"}

    ac = next(a for a in assemblies if a["code"] == "MH-AC-003")
    detail = (await client.get(f"/geo/assemblies/{ac['id']}")).json()
    assert detail["parliamentary_constituency_name"] == "Mumbai North"
    assert detail["district_name"] == "Mumbai Suburban"
