"""In-memory tool registry with JSON Schema validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
from pydantic import BaseModel, Field


class ToolRecord(BaseModel):
    name: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    auth_scope: str
    rate_limit: dict[str, int] = Field(default_factory=lambda: {"per_minute": 60})
    error_codes: list[str] = Field(default_factory=list)
    sensitive_fields: list[str] = Field(default_factory=list)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolRecord] = {}

    def register(self, tool: ToolRecord) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolRecord | None:
        return self._tools.get(name)

    def list_tools(self) -> list[ToolRecord]:
        return list(self._tools.values())

    def validate_input(self, name: str, data: dict[str, Any]) -> None:
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")
        jsonschema.validate(instance=data, schema=tool.input_schema)

    def load_seed(self, path: Path) -> None:
        with path.open() as f:
            tools = json.load(f)
        for t in tools:
            self.register(ToolRecord.model_validate(t))


registry = ToolRegistry()
