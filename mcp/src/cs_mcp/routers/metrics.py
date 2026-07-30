"""Prometheus metrics endpoint."""

from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

router = APIRouter(tags=["metrics"])

TOOL_CALLS = Counter("mcp_tool_calls_total", "Total tool calls", ["tool_name", "outcome"])
TOOL_LATENCY = Histogram("mcp_tool_latency_seconds", "Tool call latency", ["tool_name"])


@router.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
