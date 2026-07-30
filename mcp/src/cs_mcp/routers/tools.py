"""Tool registration and discovery endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from cs_mcp.registry.tool_registry import ToolRecord, registry

router = APIRouter(prefix="/tools", tags=["tools"])


class ToolRegistration(BaseModel):
    name: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    auth_scope: str
    rate_limit: dict[str, int] = Field(default_factory=lambda: {"per_minute": 60})
    error_codes: list[str] = Field(default_factory=list)
    sensitive_fields: list[str] = Field(default_factory=list)


@router.post("/register")
async def register_tool(tool: ToolRegistration) -> dict[str, str]:
    record = ToolRecord.model_validate(tool.model_dump())
    registry.register(record)
    return {"status": "registered", "name": tool.name}


@router.get("")
async def list_tools() -> dict[str, list[dict[str, Any]]]:
    return {"tools": [t.model_dump() for t in registry.list_tools()]}
