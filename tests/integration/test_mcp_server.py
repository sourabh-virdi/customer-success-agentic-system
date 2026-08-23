"""Integration tests for MCP server."""

import pytest
from httpx import ASGITransport, AsyncClient

from cs_mcp.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_list_tools():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/tools")
        assert resp.status_code == 200
        tools = resp.json()["tools"]
        assert len(tools) >= 8


@pytest.mark.asyncio
async def test_auth_exchange():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/auth/exchange",
            json={"agent_identity": "leaf_b", "scope": "diagnostics:run", "session_id": "s-1"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_kb_search_call():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/call",
            json={
                "tool_name": "kb.search",
                "input": {"query": "onboarding"},
                "agent_identity": "supervisor",
                "session_id": "s-1",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
