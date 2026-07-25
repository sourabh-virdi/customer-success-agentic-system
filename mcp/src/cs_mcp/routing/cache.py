"""TTL cache for idempotent MCP read tool calls."""

from __future__ import annotations

import time
from typing import Any


class ResponseCache:
    """Simple in-memory TTL cache keyed by tool name + input hash."""

    READ_TOOLS = {
        "kb.search",
        "billing.get_subscription",
        "diagnostics.get_report",
    }

    def __init__(self, ttl_seconds: float = 60.0) -> None:
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}

    def _key(self, tool_name: str, input: dict[str, Any]) -> str:
        return f"{tool_name}:{sorted(input.items())}"

    def get(self, tool_name: str, input: dict[str, Any]) -> dict[str, Any] | None:
        if tool_name not in self.READ_TOOLS:
            return None
        key = self._key(tool_name, input)
        entry = self._cache.get(key)
        if not entry:
            return None
        expires_at, value = entry
        if time.time() > expires_at:
            del self._cache[key]
            return None
        return value

    def set(self, tool_name: str, input: dict[str, Any], value: dict[str, Any]) -> None:
        if tool_name not in self.READ_TOOLS:
            return
        key = self._key(tool_name, input)
        self._cache[key] = (time.time() + self.ttl_seconds, value)

    def invalidate(self, tool_name: str | None = None) -> None:
        if tool_name is None:
            self._cache.clear()
            return
        keys = [k for k in self._cache if k.startswith(f"{tool_name}:")]
        for k in keys:
            del self._cache[k]
