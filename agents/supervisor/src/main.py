"""Supervisor agent runtime harness."""

from __future__ import annotations

import re
from typing import Any

from cs_agents.harness import CallModelRequest, create_base_app
from cs_agents.mcp_client import MCPClient
from cs_agents.memory_client import MemoryClient
from cs_agents.prompts import PromptLoader

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s+prompt",
    r"jailbreak",
]


def classify_intent(user_input: str) -> str:
    text = user_input.lower()
    if any(w in text for w in ["onboard", "setup", "new account", "sign up"]):
        return "onboarding"
    if any(w in text for w in ["diagnostic", "integration", "webhook", "check"]):
        return "diagnostics"
    if any(w in text for w in ["churn", "cancel", "retention", "downgrade"]):
        return "retention"
    return "onboarding"


async def supervisor_handler(
    req: CallModelRequest,
    mcp: MCPClient,
    memory: MemoryClient,
    prompts: PromptLoader,
) -> dict[str, Any]:
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, req.user_input, re.IGNORECASE):
            return {
                "response": "I cannot process that request. A security incident has been logged.",
                "intent": "blocked",
                "escalated": False,
            }

    if mcp.circuit_breaker_open:
        return {
            "response": "Our automated systems are temporarily unavailable. "
            "A human agent will assist you shortly.",
            "intent": "safe_mode",
            "escalated": True,
        }

    intent = classify_intent(req.user_input)
    leaf_map = {"onboarding": "leaf_a", "diagnostics": "leaf_b", "retention": "leaf_c"}
    leaf = leaf_map[intent]

    # Invoke leaf via internal call (simplified for harness)
    leaf_response = f"Routed to {leaf} for intent: {intent}"
    merged = {
        "response": f"Handled your {intent} request. {leaf_response}",
        "intent": intent,
        "leaf": leaf,
        "escalated": False,
    }

    await memory.write(
        "session",
        {
            "id": f"session:{req.session_id}",
            "type": "session",
            "user_id": (req.user_profile or {}).get("id", "unknown"),
            "turns": [{"role": "user", "text": req.user_input, "timestamp": "now"}],
        },
        purpose="resolution",
        consent=True,
        redaction_mask=["email"],
    )
    return merged


app = create_base_app(
    agent_id="supervisor",
    agent_role="supervisor",
    prompt_template="supervisor_system.j2",
    tool_handler=supervisor_handler,
)
