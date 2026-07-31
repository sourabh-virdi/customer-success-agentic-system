"""Export MCP tool definitions for AgentCore Gateway registration."""

import json
from pathlib import Path

SEED_PATH = Path(__file__).resolve().parents[2] / "mcp" / "tools" / "seed_tools.json"
OUTPUT_PATH = Path(__file__).resolve().parent / "gateway_tools.json"


def export_tools() -> list[dict]:
    with SEED_PATH.open() as f:
        tools = json.load(f)
    gateway_tools = []
    for t in tools:
        gateway_tools.append({
            "name": t["name"].replace(".", "__"),
            "description": f"Tool: {t['name']}",
            "inputSchema": t["input_schema"],
            "authScope": t["auth_scope"],
        })
    return gateway_tools


if __name__ == "__main__":
    tools = export_tools()
    with OUTPUT_PATH.open("w") as f:
        json.dump(tools, f, indent=2)
    print(f"Exported {len(tools)} tools to {OUTPUT_PATH}")
