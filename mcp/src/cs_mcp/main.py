"""MCP FastAPI application factory."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from cs_agents.telemetry import setup_telemetry
from cs_mcp.registry.tool_registry import registry
from cs_mcp.routers import auth, call, metrics, tools

SEED_PATH = Path(__file__).resolve().parents[2] / "tools" / "seed_tools.json"


def create_app() -> FastAPI:
    setup_telemetry("cs-mcp-server")

    app = FastAPI(
        title="Customer Success MCP Server",
        description="Tool registry, auth broker, and policy enforcement",
        version="0.1.0",
    )

    app.include_router(tools.router)
    app.include_router(call.router)
    app.include_router(auth.router)
    app.include_router(metrics.router)

    if SEED_PATH.exists():
        registry.load_seed(SEED_PATH)

    @app.on_event("startup")
    async def load_tools() -> None:
        if not registry.list_tools() and SEED_PATH.exists():
            registry.load_seed(SEED_PATH)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy"}

    FastAPIInstrumentor.instrument_app(app)
    return app


app = create_app()
