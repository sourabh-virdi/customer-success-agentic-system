"""Mock Billing backend."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

app = FastAPI(title="Mock Billing")

_subscriptions = {
    "acc-demo-001": {"plan": "Pro", "renewal_date": "2026-12-01"},
    "acc-demo-002": {"plan": "Enterprise", "renewal_date": "2026-06-15"},
}


@app.post("/tools/get_subscription")
async def get_subscription(body: dict[str, Any]) -> dict[str, Any]:
    account_id = body["account_id"]
    sub = _subscriptions.get(account_id, {"plan": "Starter", "renewal_date": "2026-01-01"})
    return {"status": "ok", **sub}


@app.post("/tools/update_plan")
async def update_plan(body: dict[str, Any]) -> dict[str, Any]:
    account_id = body["account_id"]
    plan = body["plan"]
    if account_id in _subscriptions:
        _subscriptions[account_id]["plan"] = plan
    else:
        _subscriptions[account_id] = {"plan": plan, "renewal_date": "2026-12-01"}
    return {"status": "updated", "plan": plan}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
