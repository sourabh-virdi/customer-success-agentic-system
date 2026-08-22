"""Mock CRM backend."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Mock CRM")
_accounts: dict[str, dict[str, Any]] = {}
_tickets: dict[str, dict[str, Any]] = {}


class CreateAccountRequest(BaseModel):
    company: str
    plan: str
    email: str | None = None


@app.post("/tools/create_account")
async def create_account(req: CreateAccountRequest) -> dict[str, Any]:
    account_id = f"acc-{uuid.uuid4().hex[:8]}"
    _accounts[account_id] = {"company": req.company, "plan": req.plan, "email": req.email}
    return {"status": "created", "account_id": account_id}


@app.post("/tools/update_account")
async def update_account(body: dict[str, Any]) -> dict[str, Any]:
    account_id = body["account_id"]
    fields = body.get("fields", {})
    if account_id not in _accounts:
        return {"status": "error", "error": "NOT_FOUND"}
    _accounts[account_id].update(fields)
    return {"status": "updated", "updated_fields": fields}


@app.post("/tools/create_ticket")
async def create_ticket(body: dict[str, Any]) -> dict[str, Any]:
    ticket_id = f"tkt-{uuid.uuid4().hex[:8]}"
    _tickets[ticket_id] = body
    return {"status": "created", "ticket_id": ticket_id}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
