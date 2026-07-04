"""OpenTelemetry instrumentation helpers."""

from __future__ import annotations

import logging
from contextvars import ContextVar
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Span

from cs_agents.config import settings

session_id_ctx: ContextVar[str | None] = ContextVar("session_id", default=None)
agent_id_ctx: ContextVar[str | None] = ContextVar("agent_id", default=None)

_tracer: trace.Tracer | None = None
_meter: metrics.Meter | None = None
_initialized = False


def setup_telemetry(service_name: str | None = None) -> tuple[trace.Tracer, metrics.Meter]:
    global _tracer, _meter, _initialized
    if _initialized:
        return _tracer, _meter  # type: ignore

    name = service_name or settings.otel_service_name
    resource = Resource.create({"service.name": name})
    provider = TracerProvider(resource=resource)
    if settings.otel_traces_exporter == "console":
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)

    meter_provider = MeterProvider(resource=resource)
    metrics.set_meter_provider(meter_provider)

    _tracer = trace.get_tracer(name)
    _meter = metrics.get_meter(name)
    _initialized = True
    logging.getLogger(__name__).info("Telemetry initialized for %s", name)
    return _tracer, _meter


def get_tracer() -> trace.Tracer:
    tracer, _ = setup_telemetry()
    return tracer


def get_meter() -> metrics.Meter:
    _, meter = setup_telemetry()
    return meter


def bind_context(session_id: str | None = None, agent_id: str | None = None) -> None:
    if session_id:
        session_id_ctx.set(session_id)
    if agent_id:
        agent_id_ctx.set(agent_id)


def enrich_span(span: Span, **attrs: Any) -> None:
    sid = session_id_ctx.get()
    aid = agent_id_ctx.get()
    if sid:
        span.set_attribute("session_id", sid)
    if aid:
        span.set_attribute("agent_id", aid)
    for k, v in attrs.items():
        span.set_attribute(k, v)


def record_agent_metrics(
    agent_id: str,
    latency_ms: float,
    success: bool,
    metric_type: str = "request",
) -> None:
    meter = get_meter()
    counter = meter.create_counter(f"agent.{metric_type}.count")
    histogram = meter.create_histogram(f"agent.{metric_type}.latency")
    counter.add(1, {"agent_id": agent_id, "success": str(success)})
    histogram.record(latency_ms, {"agent_id": agent_id})
