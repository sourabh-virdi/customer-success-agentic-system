"""Tests for tool registry."""

import json
from pathlib import Path

from cs_mcp.registry.tool_registry import ToolRegistry


def test_registry_load_seed():
    registry = ToolRegistry()
    seed_path = Path(__file__).resolve().parents[2] / "mcp" / "tools" / "seed_tools.json"
    registry.load_seed(seed_path)
    tools = registry.list_tools()
    assert len(tools) >= 8
    names = [t.name for t in tools]
    assert "crm.create_account" in names
    assert "diagnostics.run" in names


def test_registry_validate_input():
    registry = ToolRegistry()
    seed_path = Path(__file__).resolve().parents[2] / "mcp" / "tools" / "seed_tools.json"
    registry.load_seed(seed_path)
    registry.validate_input("diagnostics.run", {"integration_id": "int-123"})
