"""Tests for backend router."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cs_mcp.routing.backend_router import BackendRouter


@pytest.mark.asyncio
async def test_kb_search():
    router = BackendRouter()
    result = await router.call("kb.search", {"query": "onboarding"})
    assert result["status"] == "ok"
    assert len(result["results"]) >= 1


@pytest.mark.asyncio
async def test_unknown_backend_raises():
    router = BackendRouter()
    with pytest.raises(ValueError, match="No backend"):
        await router.call("unknown.tool", {})


@pytest.mark.asyncio
async def test_backend_http_call():
    router = BackendRouter()
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"status": "created", "account_id": "acc-1"}

    with patch("cs_mcp.routing.backend_router.httpx.AsyncClient") as mock_client:
        instance = AsyncMock()
        instance.post.return_value = mock_resp
        mock_client.return_value.__aenter__.return_value = instance

        result = await router.call("crm.create_account", {"company": "X", "plan": "Pro"})
        assert result["account_id"] == "acc-1"
