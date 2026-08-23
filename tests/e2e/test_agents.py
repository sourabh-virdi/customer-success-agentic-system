"""Tests for agent harness and supervisor handler."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "agents" / "supervisor" / "src"))

from cs_agents.harness import CallModelRequest
from main import app, supervisor_handler  # noqa: E402


@pytest.mark.asyncio
async def test_supervisor_session_start():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/runtime/session/start",
            json={"user_id": "u-1", "agent_role": "supervisor"},
        )
        assert resp.status_code == 200
        assert "session_id" in resp.json()


@pytest.mark.asyncio
async def test_supervisor_call_model():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("cs_agents.memory_client.MemoryClient.write", new_callable=AsyncMock) as mock_write:
            mock_write.return_value = {"status": "written"}
            resp = await client.post(
                "/runtime/session/call_model",
                json={"session_id": "s-1", "user_input": "help with onboarding"},
            )
            assert resp.status_code == 200
            assert resp.json()["intent"] == "onboarding"


@pytest.mark.asyncio
async def test_supervisor_safe_mode():
    req = CallModelRequest(session_id="s-1", user_input="help with onboarding")
    mcp = MagicMock()
    mcp.circuit_breaker_open = True
    memory = AsyncMock()
    from cs_agents.prompts import PromptLoader

    result = await supervisor_handler(req, mcp, memory, PromptLoader())
    assert result["intent"] == "safe_mode"
    assert result["escalated"] is True


@pytest.mark.asyncio
async def test_export_gateway_tools():
    from infra.agentcore_configs.export_gateway_tools import export_tools

    tools = export_tools()
    assert len(tools) >= 8
    assert tools[0]["name"].startswith("crm__") or "crm" in tools[0]["name"]
