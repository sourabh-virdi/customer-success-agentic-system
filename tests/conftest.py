"""Shared pytest fixtures."""

import sys
from pathlib import Path

import pytest

from cs_agents.circuit_breaker import CircuitState

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for p in ["agents/shared", "mcp/src", "memory/api", "evaluations", "mocks"]:
    sys.path.insert(0, str(ROOT / p))


@pytest.fixture(autouse=True)
def reset_circuit_breakers():
    from cs_mcp.routing import backend_router as br

    for breaker in br._breakers._breakers.values():
        breaker.state = CircuitState.CLOSED
        breaker.failure_count = 0
    yield
