"""Leaf C - Retention agent."""

from __future__ import annotations

from cs_agents.harness import CallModelRequest, create_base_app
from cs_agents.mcp_client import MCPClient
from cs_agents.memory_client import MemoryClient
from cs_agents.prompts import PromptLoader


async def retention_handler(
    req: CallModelRequest,
    mcp: MCPClient,
    memory: MemoryClient,
    prompts: PromptLoader,
) -> dict[str, Any]:
    profile = req.user_profile or {"churn_score": 0.5, "id": "user:u-002"}
    churn_score = profile.get("churn_score", 0.5)
    account_id = "acc-demo-002"

    await mcp.exchange_token(scope="billing:read", session_id=req.session_id)
    subscription = await mcp.call_tool(
        "billing.get_subscription",
        {"account_id": account_id},
        session_id=req.session_id,
    )

    offer = "20% discount for 3 months" if churn_score > 0.5 else "Standard renewal reminder"
    ticket_id = None
    if churn_score > 0.7:
        ticket = await mcp.call_tool(
            "crm.create_ticket",
            {"account_id": account_id, "subject": "High churn risk", "priority": "high"},
            session_id=req.session_id,
        )
        ticket_id = ticket.get("ticket_id")

    return {
        "response": f"Retention offer: {offer}. Plan: {subscription.get('plan')}.",
        "offer": offer,
        "ticket_id": ticket_id,
        "churn_score": churn_score,
    }


app = create_base_app(
    agent_id="leaf_c_retention",
    agent_role="leaf_c_retention",
    prompt_template="leaf_c_retention.j2",
    tool_handler=retention_handler,
)
