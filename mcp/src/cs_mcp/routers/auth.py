"""Agent identity token exchange endpoint."""

from __future__ import annotations

import os
import secrets
import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from cs_mcp.policies.enforcement import audit_logger

router = APIRouter(prefix="/auth", tags=["auth"])

TOKEN_TTL_MINUTES = int(os.getenv("TOKEN_TTL_MINUTES", "10"))
_tokens: dict[str, dict[str, Any]] = {}


class AuthExchangeRequest(BaseModel):
    agent_identity: str
    scope: str = "*"
    session_id: str


class AuthExchangeResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = Field(description="Seconds until expiry")
    scope: str
    session_id: str


@router.post("/exchange", response_model=AuthExchangeResponse)
async def exchange_token(request: AuthExchangeRequest) -> AuthExchangeResponse:
    if not request.agent_identity:
        raise HTTPException(status_code=400, detail="agent_identity required")

    token = secrets.token_urlsafe(32)
    expires_in = TOKEN_TTL_MINUTES * 60
    _tokens[token] = {
        "agent_identity": request.agent_identity,
        "scope": request.scope,
        "session_id": request.session_id,
        "expires_at": time.time() + expires_in,
    }

    trace_id = str(uuid.uuid4())
    audit_logger.log(
        request.agent_identity, request.session_id, "auth.exchange", "success", trace_id,
        {"scope": request.scope},
    )

    return AuthExchangeResponse(
        access_token=token,
        expires_in=expires_in,
        scope=request.scope,
        session_id=request.session_id,
    )
