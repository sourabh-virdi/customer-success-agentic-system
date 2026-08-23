"""E2E tests for supervisor intent routing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "agents" / "supervisor" / "src"))

from main import classify_intent  # noqa: E402


def test_route_onboarding():
    assert classify_intent("I need help with onboarding") == "onboarding"


def test_route_diagnostics():
    assert classify_intent("Run integration diagnostic check") == "diagnostics"


def test_route_retention():
    assert classify_intent("I want to cancel due to churn concerns") == "retention"
