"""Extended memory API tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from memory.api.main import app


@pytest.mark.asyncio
async def test_read_write_delete_cycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        write = await client.post(
            "/memory/session",
            json={
                "id": "session:cycle-1",
                "type": "session",
                "user_id": "u-1",
                "turns": [],
                "consent": True,
            },
            params={"agent_id": "supervisor", "purpose": "resolution"},
        )
        assert write.status_code == 200

        read = await client.get(
            "/memory/session/cycle-1",
            params={"agent_id": "supervisor", "purpose": "resolution"},
        )
        assert read.status_code == 200

        delete = await client.delete(
            "/memory/session/cycle-1",
            params={"agent_id": "supervisor", "purpose": "forget"},
        )
        assert delete.status_code == 200


@pytest.mark.asyncio
async def test_user_profile_scope_alias():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/memory/user_profile",
            json={
                "id": "user:u-10",
                "type": "profile",
                "company": "Acme",
                "plan": "Pro",
                "consent": True,
            },
            params={"agent_id": "leaf_a", "purpose": "onboarding"},
        )
        assert resp.status_code == 200
        assert resp.json()["key"].startswith("profile:")


@pytest.mark.asyncio
async def test_retention_config_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/config/retention")
        assert resp.status_code == 200
        assert resp.json()["session_days"] == 30


@pytest.mark.asyncio
async def test_invalid_scope():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/memory/invalid/x",
            params={"agent_id": "a", "purpose": "p"},
        )
        assert resp.status_code == 400
