"""Route tool calls to mock backend services."""

from __future__ import annotations

import os
from typing import Any

import httpx

from cs_agents.circuit_breaker import CircuitBreakerRegistry
from cs_mcp.routing.cache import ResponseCache

CRM_URL = os.getenv("CRM_MOCK_URL", "http://localhost:8010")
BILLING_URL = os.getenv("BILLING_MOCK_URL", "http://localhost:8011")
DIAGNOSTICS_MOCK_URL = os.getenv("DIAGNOSTICS_MOCK_URL", "http://localhost:8012")

_breakers = CircuitBreakerRegistry()
_response_cache = ResponseCache(ttl_seconds=60.0)


class BackendRouter:
    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout

    def _backend_url(self, tool_name: str) -> str | None:
        prefix = tool_name.split(".")[0]
        mapping = {
            "crm": CRM_URL,
            "billing": BILLING_URL,
            "diagnostics": DIAGNOSTICS_MOCK_URL,
        }
        return mapping.get(prefix)

    async def call(self, tool_name: str, input: dict[str, Any]) -> dict[str, Any]:
        prefix = tool_name.split(".")[0]
        breaker = _breakers.get(prefix)

        cached = _response_cache.get(tool_name, input)
        if cached is not None:
            return cached

        if tool_name == "kb.search":
            result = {
                "status": "ok",
                "results": [
                    {"title": "Getting Started", "snippet": f"Results for: {input.get('query', '')}"}
                ],
            }
            _response_cache.set(tool_name, input, result)
            return result

        backend = self._backend_url(tool_name)
        if not backend:
            raise ValueError(f"No backend for tool: {tool_name}")

        if not breaker.allow_request():
            raise RuntimeError(f"Circuit breaker open for {prefix}")

        action = tool_name.split(".", 1)[1]
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{backend}/tools/{action}", json=input)
                resp.raise_for_status()
                breaker.record_success()
                result = resp.json()
                _response_cache.set(tool_name, input, result)
                return result
            except Exception:
                breaker.record_failure()
                raise

    def any_circuit_open(self) -> bool:
        return _breakers.any_open()
