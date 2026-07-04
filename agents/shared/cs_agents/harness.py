"""Shared agent runtime harness base."""

from __future__ import annotations

import time
import uuid
from typing import Any

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

from cs_agents.mcp_client import MCPClient
from cs_agents.memory_client import MemoryClient
from cs_agents.prompts import PromptLoader
from cs_agents.telemetry import bind_context, get_tracer, record_agent_metrics, setup_telemetry


class SessionStartRequest(BaseModel):
    session_id: str | None = None
    user_id: str
    agent_role: str


class CallModelRequest(BaseModel):
    session_id: str
    user_input: str
    session_memory: dict[str, Any] | None = None
    user_profile: dict[str, Any] | None = None


class InvokeAgentRequest(BaseModel):
    leaf_agent: str
    input: str
    session_id: str
    purpose: str
    timeout: float = 30.0


def create_base_app(
    agent_id: str,
    agent_role: str,
    prompt_template: str,
    leaf_port_map: dict[str, int] | None = None,
    tool_handler: Any = None,
) -> FastAPI:
    setup_telemetry(f"cs-agent-{agent_role}")
    app = FastAPI(title=f"Agent {agent_role}", version="0.1.0")
    sessions: dict[str, dict[str, Any]] = {}
    mcp = MCPClient(agent_identity=agent_id)
    memory = MemoryClient(agent_id=agent_id)
    prompts = PromptLoader()
    leaf_ports = leaf_port_map or {
        "leaf_a": 8021,
        "leaf_b": 8022,
        "leaf_c": 8023,
    }

    @app.post("/runtime/session/start")
    async def start_session(req: SessionStartRequest) -> dict[str, Any]:
        sid = req.session_id or str(uuid.uuid4())
        sessions[sid] = {"user_id": req.user_id, "agent_role": req.agent_role, "started": time.time()}
        bind_context(session_id=sid, agent_id=agent_id)
        return {"session_id": sid, "status": "started"}

    @app.post("/runtime/session/call_model")
    async def call_model(req: CallModelRequest) -> dict[str, Any]:
        bind_context(session_id=req.session_id, agent_id=agent_id)
        tracer = get_tracer()
        start = time.time()
        with tracer.start_as_current_span("call_model"):
            prompt = prompts.render(
                prompt_template,
                user_input=req.user_input,
                session_memory=req.session_memory or {},
                user_profile=req.user_profile or {},
                integration_id=req.user_input,
                churn_score=(req.user_profile or {}).get("churn_score", 0.0),
            )
            result: dict[str, Any] = {"prompt": prompt, "response": ""}
            if tool_handler:
                result = await tool_handler(req, mcp, memory, prompts)
            latency = (time.time() - start) * 1000
            record_agent_metrics(agent_id, latency, True)
            return {"session_id": req.session_id, **result}

    @app.post("/runtime/session/invoke_agent")
    async def invoke_agent(req: InvokeAgentRequest) -> dict[str, Any]:
        port = leaf_ports.get(req.leaf_agent)
        if not port:
            return {"status": "error", "error": f"Unknown leaf: {req.leaf_agent}"}
        async with httpx.AsyncClient(timeout=req.timeout) as client:
            resp = await client.post(
                f"http://localhost:{port}/runtime/session/call_model",
                json={
                    "session_id": req.session_id,
                    "user_input": req.input,
                },
            )
            resp.raise_for_status()
            return resp.json()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy", "agent": agent_id}

    return app
