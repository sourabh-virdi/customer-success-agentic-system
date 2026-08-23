"""Additional MCP server endpoint tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from cs_mcp.main import app
from cs_mcp.policies.enforcement import rate_limiter


@pytest.mark.asyncio
async def test_register_tool():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/tools/register",
            json={
                "name": "custom.tool",
                "input_schema": {"type": "object"},
                "output_schema": {"type": "object"},
                "auth_scope": "custom:read",
            },
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_call_unknown_tool():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/call",
            json={
                "tool_name": "nonexistent.tool",
                "input": {},
                "agent_identity": "test",
                "session_id": "s-1",
            },
        )
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_call_validation_error():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/call",
            json={
                "tool_name": "diagnostics.run",
                "input": {"unexpected": "field"},
                "agent_identity": "test",
                "session_id": "s-1",
            },
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_metrics_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/metrics")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_rate_limit_exceeded():
    rate_limiter._buckets.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for _ in range(201):
            await client.post(
                "/call",
                json={
                    "tool_name": "kb.search",
                    "input": {"query": "x"},
                    "agent_identity": "rate-test-agent",
                    "session_id": "s-rate",
                },
            )
        resp = await client.post(
            "/call",
            json={
                "tool_name": "kb.search",
                "input": {"query": "x"},
                "agent_identity": "rate-test-agent",
                "session_id": "s-rate",
            },
        )
        assert resp.status_code == 429
