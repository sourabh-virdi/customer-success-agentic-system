"""Integration tests for memory API."""

import pytest
from httpx import ASGITransport, AsyncClient

from memory.api.main import app


@pytest.mark.asyncio
async def test_memory_write_with_pii_redaction():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/memory/session",
            json={
                "id": "session:test-1",
                "type": "session",
                "user_id": "u-1",
                "turns": [{"role": "user", "text": "email test@example.com", "timestamp": "now"}],
                "consent": True,
            },
            params={"agent_id": "supervisor", "purpose": "resolution"},
        )
        assert resp.status_code == 200
        record = resp.json()["record"]
        assert "test@example.com" not in str(record)


@pytest.mark.asyncio
async def test_profile_requires_consent():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/memory/profile",
            json={"id": "user:u-1", "type": "profile", "company": "Acme", "plan": "Pro", "consent": False},
            params={"agent_id": "leaf_a", "purpose": "onboarding"},
        )
        assert resp.status_code == 403
