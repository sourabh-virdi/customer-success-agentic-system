"""Tests for memory client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cs_agents.memory_client import MemoryClient


@pytest.mark.asyncio
async def test_memory_read():
    client = MemoryClient(base_url="http://mem.test", agent_id="leaf_a")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"id": "session:1"}

    with patch("cs_agents.memory_client.httpx.AsyncClient") as mock_client:
        instance = AsyncMock()
        instance.get.return_value = mock_resp
        mock_client.return_value.__aenter__.return_value = instance

        result = await client.read("session", "1", purpose="resolution")
        assert result["id"] == "session:1"


@pytest.mark.asyncio
async def test_memory_write_and_delete():
    client = MemoryClient(base_url="http://mem.test")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"status": "written"}

    with patch("cs_agents.memory_client.httpx.AsyncClient") as mock_client:
        instance = AsyncMock()
        instance.post.return_value = mock_resp
        instance.delete.return_value = mock_resp
        mock_client.return_value.__aenter__.return_value = instance

        await client.write("session", {"id": "session:1"}, purpose="test", consent=True)
        await client.delete("session", "1", purpose="forget")
