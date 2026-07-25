"""Policy enforcement: PII filter, rate limiting, audit logging."""

from __future__ import annotations

import json
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cs_agents.pii import load_pii_patterns, redact_dict

PII_PATTERNS_PATH = Path(__file__).resolve().parents[3] / "policies" / "pii_patterns.yaml"


@dataclass
class AuditEntry:
    audit_id: str
    timestamp: float
    agent_id: str
    session_id: str
    tool_name: str
    outcome: str
    trace_id: str
    details: dict[str, Any] = field(default_factory=dict)


class AuditLogger:
    """Append-only audit log."""

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def log(
        self,
        agent_id: str,
        session_id: str,
        tool_name: str,
        outcome: str,
        trace_id: str = "",
        details: dict[str, Any] | None = None,
    ) -> AuditEntry:
        entry = AuditEntry(
            audit_id=str(uuid.uuid4()),
            timestamp=time.time(),
            agent_id=agent_id,
            session_id=session_id,
            tool_name=tool_name,
            outcome=outcome,
            trace_id=trace_id or str(uuid.uuid4()),
            details=details or {},
        )
        self._entries.append(entry)
        return entry

    def get_entries(self) -> list[AuditEntry]:
        return list(self._entries)

    def to_json_lines(self) -> str:
        return "\n".join(json.dumps(e.__dict__) for e in self._entries)


class PIIFilter:
    def __init__(self) -> None:
        self.patterns = load_pii_patterns(PII_PATTERNS_PATH)

    def apply(self, data: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        return redact_dict(data, self.patterns)


class RateLimiter:
    """Token bucket per (agent_id, tool_name)."""

    def __init__(self) -> None:
        self._buckets: dict[str, list[float]] = defaultdict(list)

    def allow(self, agent_id: str, tool_name: str, per_minute: int) -> bool:
        key = f"{agent_id}:{tool_name}"
        now = time.time()
        window = self._buckets[key]
        self._buckets[key] = [t for t in window if now - t < 60]
        if len(self._buckets[key]) >= per_minute:
            return False
        self._buckets[key].append(now)
        return True


audit_logger = AuditLogger()
pii_filter = PIIFilter()
rate_limiter = RateLimiter()
