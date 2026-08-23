"""Tests for telemetry helpers."""

from cs_agents.telemetry import (
    bind_context,
    enrich_span,
    get_meter,
    get_tracer,
    record_agent_metrics,
    setup_telemetry,
)


def test_setup_telemetry_idempotent():
    tracer1, meter1 = setup_telemetry("test-service")
    tracer2, meter2 = setup_telemetry("test-service")
    assert tracer1 is tracer2
    assert meter1 is meter2


def test_get_tracer_and_meter():
    assert get_tracer() is not None
    assert get_meter() is not None


def test_bind_context_and_record_metrics():
    bind_context(session_id="sess-1", agent_id="agent-1")
    record_agent_metrics("agent-1", 100.0, True)


class _FakeSpan:
    def __init__(self) -> None:
        self.attrs: dict = {}

    def set_attribute(self, key, value) -> None:
        self.attrs[key] = value


def test_enrich_span():
    bind_context(session_id="s-99", agent_id="sup")
    span = _FakeSpan()
    enrich_span(span, action="test")
    assert span.attrs["session_id"] == "s-99"
    assert span.attrs["action"] == "test"
