"""Mock Diagnostics backend."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI

app = FastAPI(title="Mock Diagnostics")

_reports: dict[str, dict[str, Any]] = {}


@app.post("/tools/run")
async def run_diagnostics(body: dict[str, Any]) -> dict[str, Any]:
    integration_id = body["integration_id"]
    checks = [
        {"name": "auth", "status": "ok"},
        {"name": "webhook", "status": "fail" if "fail" in integration_id else "ok"},
        {"name": "rate_limit", "status": "ok"},
    ]
    report_id = f"diag-{uuid.uuid4().hex[:8]}"
    status = "passed" if all(c["status"] == "ok" for c in checks) else "failed"
    _reports[report_id] = {
        "status": status,
        "checks": checks,
        "report_url": f"https://internal/reports/{report_id}",
    }
    return {"status": status, "checks": checks, "report_id": report_id}


@app.post("/tools/get_report")
async def get_report(body: dict[str, Any]) -> dict[str, Any]:
    report_id = body["report_id"]
    report = _reports.get(report_id)
    if not report:
        return {"status": "error", "error": "NOT_FOUND"}
    return {"status": "ok", **report}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
