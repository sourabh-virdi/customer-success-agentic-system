"""Memory API client for agents."""

from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from cs_agents.config import settings


class MemoryClient:
    def __init__(self, base_url: str | None = None, agent_id: str | None = None) -> None:
        self.base_url = (base_url or settings.memory_api_url).rstrip("/")
        self.agent_id = agent_id or settings.agent_identity
        self.timeout = 30.0

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def read(self, scope: str, record_id: str, purpose: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(
                f"{self.base_url}/memory/{scope}/{record_id}",
                params={"agent_id": self.agent_id, "purpose": purpose},
            )
            resp.raise_for_status()
            return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
    async def write(
        self,
        scope: str,
        record: dict[str, Any],
        purpose: str,
        consent: bool = False,
        redaction_mask: list[str] | None = None,
    ) -> dict[str, Any]:
        payload = {
            **record,
            "purpose": purpose,
            "consent": consent,
            "redaction_mask": redaction_mask or [],
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/memory/{scope}",
                json=payload,
                params={"agent_id": self.agent_id, "purpose": purpose},
            )
            resp.raise_for_status()
            return resp.json()

    async def delete(self, scope: str, record_id: str, purpose: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.delete(
                f"{self.base_url}/memory/{scope}/{record_id}",
                params={"agent_id": self.agent_id, "purpose": purpose},
            )
            resp.raise_for_status()
            return resp.json()
