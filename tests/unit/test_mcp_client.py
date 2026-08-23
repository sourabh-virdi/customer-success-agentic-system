"""Tests for MCP client with mocked HTTP."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tenacity import RetryError

from cs_agents.mcp_client import MCPClient, ToolDefinition


@pytest.mark.asyncio
async def test_exchange_token():
    client = MCPClient(base_url="http://mcp.test")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"access_token": "tok-abc"}

    with patch("cs_agents.mcp_client.httpx.AsyncClient") as mock_client:
        instance = AsyncMock()
        instance.post.return_value = mock_resp
        mock_client.return_value.__aenter__.return_value = instance

        token = await client.exchange_token(scope="crm:write", session_id="s-1")
        assert token == "tok-abc"


@pytest.mark.asyncio
async def test_list_tools():
    client = MCPClient(base_url="http://mcp.test")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "tools": [
            {
                "name": "kb.search",
                "input_schema": {"type": "object"},
                "output_schema": {"type": "object"},
                "auth_scope": "kb:read",
            }
        ]
    }

    with patch("cs_agents.mcp_client.httpx.AsyncClient") as mock_client:
        instance = AsyncMock()
        instance.get.return_value = mock_resp
        mock_client.return_value.__aenter__.return_value = instance

        tools = await client.list_tools()
        assert len(tools) == 1
        assert isinstance(tools[0], ToolDefinition)


@pytest.mark.asyncio
async def test_circuit_breaker_open_raises():
    client = MCPClient(base_url="http://mcp.test")
    breaker = client._circuit_breakers.get("crm")
    for _ in range(5):
        breaker.record_failure()
    with pytest.raises((RuntimeError, RetryError)):
        await client.call_tool("crm.create_account", {}, "s-1")
