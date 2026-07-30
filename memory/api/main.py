"""AgentCore Memory CRUD API."""

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException, Query
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from cs_agents.pii import redact_dict
from cs_agents.telemetry import setup_telemetry

app = FastAPI(title="AgentCore Memory API", version="0.1.0")
_store: dict[str, dict[str, Any]] = {}
_audit: list[dict[str, Any]] = []

ALLOWED_SCOPES = {"session", "profile", "user_profile", "diagnostic", "aggregate"}
SCOPE_ALIASES = {"user_profile": "profile"}

RETENTION_PATH = Path(__file__).resolve().parents[1] / "retention_config.yaml"


def _normalize_scope(scope: str) -> str:
    return SCOPE_ALIASES.get(scope, scope)


def _load_retention_config() -> dict[str, Any]:
    if RETENTION_PATH.exists():
        with RETENTION_PATH.open() as f:
            return yaml.safe_load(f) or {}
    return {"session_days": 30, "profile_days": 365}


retention_config = _load_retention_config()


def _key(scope: str, record_id: str) -> str:
    return f"{scope}:{record_id}"


@app.on_event("startup")
async def startup() -> None:
    setup_telemetry("cs-memory-api")


@app.get("/config/retention")
async def get_retention_config() -> dict[str, Any]:
    return retention_config


@app.get("/memory/{scope}/{record_id}")
async def read_memory(
    scope: str,
    record_id: str,
    agent_id: str = Query(...),
    purpose: str = Query(...),
) -> dict[str, Any]:
    if scope not in ALLOWED_SCOPES:
        raise HTTPException(status_code=400, detail="Invalid scope")
    scope = _normalize_scope(scope)
    key = _key(scope, record_id)
    if key not in _store:
        raise HTTPException(status_code=404, detail="Record not found")
    _audit.append({"action": "read", "agent_id": agent_id, "purpose": purpose, "key": key})
    return _store[key]


@app.post("/memory/{scope}")
async def write_memory(
    scope: str,
    record: dict[str, Any],
    agent_id: str = Query(...),
    purpose: str = Query(...),
) -> dict[str, Any]:
    if scope not in ALLOWED_SCOPES:
        raise HTTPException(status_code=400, detail="Invalid scope")
    scope = _normalize_scope(scope)

    consent = record.get("consent", False)
    if scope == "profile" and not consent:
        raise HTTPException(status_code=403, detail="Consent required for profile writes")

    redacted, matched = redact_dict(record)
    record_id = redacted.get("id", "").split(":")[-1] if ":" in redacted.get("id", "") else str(uuid.uuid4())
    key = _key(scope, record_id)

    redacted["purpose"] = purpose
    redacted["redaction_mask"] = list(set(redacted.get("redaction_mask", []) + matched))
    redacted["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    redacted["retention_days"] = retention_config.get(f"{scope}_days", 30)
    _store[key] = redacted
    _audit.append({"action": "write", "agent_id": agent_id, "purpose": purpose, "key": key})
    return {"status": "written", "key": key, "record": redacted}


@app.delete("/memory/{scope}/{record_id}")
async def delete_memory(
    scope: str,
    record_id: str,
    agent_id: str = Query(...),
    purpose: str = Query(...),
) -> dict[str, Any]:
    if scope not in ALLOWED_SCOPES:
        raise HTTPException(status_code=400, detail="Invalid scope")
    scope = _normalize_scope(scope)
    key = _key(scope, record_id)
    if key not in _store:
        raise HTTPException(status_code=404, detail="Record not found")
    del _store[key]
    _audit.append({"action": "delete", "agent_id": agent_id, "purpose": purpose, "key": key})
    return {"status": "deleted", "key": key}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


FastAPIInstrumentor.instrument_app(app)
