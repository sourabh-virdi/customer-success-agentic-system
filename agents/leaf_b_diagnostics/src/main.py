"""Leaf B - Diagnostics agent."""

from __future__ import annotations

from cs_agents.harness import CallModelRequest, create_base_app
from cs_agents.mcp_client import MCPClient
from cs_agents.memory_client import MemoryClient
from cs_agents.prompts import PromptLoader


async def diagnostics_handler(
    req: CallModelRequest,
    mcp: MCPClient,
    memory: MemoryClient,
    prompts: PromptLoader,
) -> dict[str, Any]:
    integration_id = req.user_input if req.user_input.startswith("int-") else "int-123"
    await mcp.exchange_token(scope="diagnostics:run", session_id=req.session_id)
    result = await mcp.call_tool(
        "diagnostics.run",
        {"integration_id": integration_id},
        session_id=req.session_id,
    )
    report_id = result.get("report_id", "diag-unknown")
    await memory.write(
        "diagnostic",
        {
            "id": f"diag:{report_id}",
            "type": "diagnostic",
            "integration_id": integration_id,
            "status": result.get("status", "unknown"),
            "checks": result.get("checks", []),
            "report_url": f"https://internal/reports/{report_id}",
        },
        purpose="diagnostic",
        consent=True,
        redaction_mask=["api_key", "webhook_url"],
    )
    failed = [c for c in result.get("checks", []) if c.get("status") == "fail"]
    remediation = "Check webhook configuration and retry." if failed else "All checks passed."
    return {
        "response": f"Diagnostics {result.get('status')}. {remediation}",
        "tool_result": result,
        "remediation": remediation,
    }


app = create_base_app(
    agent_id="leaf_b_diagnostics",
    agent_role="leaf_b_diagnostics",
    prompt_template="leaf_b_diagnostics.j2",
    tool_handler=diagnostics_handler,
)
