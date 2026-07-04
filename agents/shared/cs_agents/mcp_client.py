"""Typed MCP client with retry, circuit breaker, and schema validation."""

from __future__ import annotations

import uuid
from typing import Any

import httpx
import jsonschema
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from cs_agents.circuit_breaker import CircuitBreakerRegistry
from cs_agents.config import settings


class ToolDefinition(BaseModel):
    name: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    auth_scope: str
    rate_limit: dict[str, int] = Field(default_factory=lambda: {"per_minute": 60})
    error_codes: list[str] = Field(default_factory=list)
    sensitive_fields: list[str] = Field(default_factory=list)


class MCPClient:
    def __init__(
        self,
        base_url: str | None = None,
        agent_identity: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = (base_url or settings.mcp_base_url).rstrip("/")
        self.agent_identity = agent_identity or settings.agent_identity
        self.timeout = timeout
        self._token: str | None = None
        self._circuit_breakers = CircuitBreakerRegistry()

    def _backend_for_tool(self, tool_name: str) -> str:
        return tool_name.split(".")[0] if "." in tool_name else "default"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def exchange_token(
        self, agent_identity: str | None = None, scope: str = "*", session_id: str = ""
    ) -> str:
        identity = agent_identity or self.agent_identity
        breaker = self._circuit_breakers.get("auth")
        if not breaker.allow_request():
            raise RuntimeError("MCP auth circuit breaker is open")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/auth/exchange",
                    json={
                        "agent_identity": identity,
                        "scope": scope,
                        "session_id": session_id or str(uuid.uuid4()),
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                self._token = data["access_token"]
                breaker.record_success()
                return self._token
            except Exception:
                breaker.record_failure()
                raise

    async def list_tools(self) -> list[ToolDefinition]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/tools")
            resp.raise_for_status()
            return [ToolDefinition.model_validate(t) for t in resp.json()["tools"]]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def call_tool(
        self,
        tool_name: str,
        input: dict[str, Any],
        session_id: str,
        agent_identity: str | None = None,
    ) -> dict[str, Any]:
        backend = self._backend_for_tool(tool_name)
        breaker = self._circuit_breakers.get(backend)
        if not breaker.allow_request():
            raise RuntimeError(f"Circuit breaker open for backend: {backend}")

        payload = {
            "tool_name": tool_name,
            "input": input,
            "agent_identity": agent_identity or self.agent_identity,
            "session_id": session_id,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/call", json=payload)
                resp.raise_for_status()
                result = resp.json()
                if result.get("status") == "error":
                    breaker.record_failure()
                    raise RuntimeError(result.get("error", "Tool call failed"))
                output = result.get("output", {})
                await self._validate_output(tool_name, output)
                breaker.record_success()
                return output
            except Exception:
                breaker.record_failure()
                raise

    async def _validate_output(self, tool_name: str, output: dict[str, Any]) -> None:
        tools = await self.list_tools()
        tool = next((t for t in tools if t.name == tool_name), None)
        if tool and tool.output_schema:
            jsonschema.validate(instance=output, schema=tool.output_schema)

    @property
    def circuit_breaker_open(self) -> bool:
        return self._circuit_breakers.any_open()
