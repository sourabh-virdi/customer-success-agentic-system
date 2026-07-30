"""Tool invocation endpoint."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from cs_mcp.policies.enforcement import audit_logger, pii_filter, rate_limiter
from cs_mcp.registry.tool_registry import registry
from cs_mcp.routing.backend_router import BackendRouter

router = APIRouter(tags=["call"])
backend_router = BackendRouter()


class ToolCallRequest(BaseModel):
    tool_name: str
    input: dict[str, Any]
    agent_identity: str
    session_id: str


class ToolCallResponse(BaseModel):
    status: str
    output: dict[str, Any] | None = None
    error: str | None = None
    trace_id: str


@router.post("/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest) -> ToolCallResponse:
    trace_id = str(uuid.uuid4())
    tool = registry.get(request.tool_name)
    if not tool:
        audit_logger.log(
            request.agent_identity, request.session_id, request.tool_name, "error", trace_id,
            {"reason": "unknown_tool"},
        )
        raise HTTPException(status_code=404, detail=f"Unknown tool: {request.tool_name}")

    per_minute = tool.rate_limit.get("per_minute", 60)
    if not rate_limiter.allow(request.agent_identity, request.tool_name, per_minute):
        audit_logger.log(
            request.agent_identity, request.session_id, request.tool_name, "rate_limited", trace_id
        )
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        registry.validate_input(request.tool_name, request.input)
    except Exception as e:
        audit_logger.log(
            request.agent_identity, request.session_id, request.tool_name, "validation_error",
            trace_id, {"error": str(e)},
        )
        raise HTTPException(status_code=400, detail=str(e)) from e

    redacted_input, pii_matched = pii_filter.apply(request.input)

    try:
        output = await backend_router.call(request.tool_name, redacted_input)
        audit_logger.log(
            request.agent_identity, request.session_id, request.tool_name, "success", trace_id,
            {"pii_redacted": pii_matched},
        )
        return ToolCallResponse(status="ok", output=output, trace_id=trace_id)
    except RuntimeError as e:
        audit_logger.log(
            request.agent_identity, request.session_id, request.tool_name, "circuit_open", trace_id
        )
        return ToolCallResponse(status="error", error=str(e), trace_id=trace_id)
    except Exception as e:
        audit_logger.log(
            request.agent_identity, request.session_id, request.tool_name, "error", trace_id,
            {"error": str(e)},
        )
        return ToolCallResponse(status="error", error=str(e), trace_id=trace_id)
