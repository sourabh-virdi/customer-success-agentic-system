"""Leaf A - Onboarding agent."""

from __future__ import annotations

from cs_agents.harness import CallModelRequest, create_base_app
from cs_agents.mcp_client import MCPClient
from cs_agents.memory_client import MemoryClient
from cs_agents.prompts import PromptLoader


async def onboarding_handler(
    req: CallModelRequest,
    mcp: MCPClient,
    memory: MemoryClient,
    prompts: PromptLoader,
) -> dict[str, Any]:
    await mcp.exchange_token(scope="crm:write", session_id=req.session_id)
    result = await mcp.call_tool(
        "crm.create_account",
        {"company": "NewCo", "plan": "Pro", "email": "user@example.com"},
        session_id=req.session_id,
    )
    await memory.write(
        "profile",
        {
            "id": "user:new",
            "type": "profile",
            "company": "NewCo",
            "plan": "Pro",
            "integrations": [],
            "preferences": {},
            "churn_score": 0.0,
        },
        purpose="onboarding",
        consent=True,
        redaction_mask=["email"],
    )
    return {
        "response": f"Onboarding complete. Account {result.get('account_id')} created.",
        "tool_result": result,
    }


app = create_base_app(
    agent_id="leaf_a_onboarding",
    agent_role="leaf_a_onboarding",
    prompt_template="leaf_a_onboarding.j2",
    tool_handler=onboarding_handler,
)
