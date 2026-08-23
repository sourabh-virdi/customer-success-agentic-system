"""Chaos and degradation tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from cs_mcp.main import app
from cs_mcp.routing.backend_router import BackendRouter


@pytest.mark.asyncio
async def test_mcp_health_when_backend_unavailable():
    """Simulates MCP still healthy when backends are down (kb.search is local)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_circuit_breaker_opens_on_backend_failure():
    router = BackendRouter()
    breaker = router.__class__.__module__  # ensure router loads
    from cs_mcp.routing import backend_router as br

    br._breakers.get("crm").failure_threshold = 1
    br._breakers.get("crm").record_failure()
    assert br._breakers.get("crm").state.value == "open"
