"""Example AgentCore Identity → MCP token exchange flow."""

import asyncio
import os
import uuid

from cs_agents.mcp_client import MCPClient


async def main() -> None:
    session_id = str(uuid.uuid4())
    agent_identity = os.getenv("AGENT_IDENTITY", "leaf_b_diagnostics")
    scope = "diagnostics:run"

    client = MCPClient(agent_identity=agent_identity)
    token = await client.exchange_token(scope=scope, session_id=session_id)
    print(f"Exchanged token for {agent_identity} (scope={scope})")
    print(f"Token prefix: {token[:16]}...")

    result = await client.call_tool(
        "diagnostics.run",
        {"integration_id": "int-123"},
        session_id=session_id,
    )
    print(f"Tool result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
