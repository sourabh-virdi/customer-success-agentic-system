"""Tests for mock backend services."""

import pytest
from httpx import ASGITransport, AsyncClient

from mocks.billing.main import app as billing_app
from mocks.crm.main import app as crm_app
from mocks.diagnostics.main import app as diag_app


@pytest.mark.asyncio
async def test_crm_create_account():
    transport = ASGITransport(app=crm_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/tools/create_account",
            json={"company": "TestCo", "plan": "Pro"},
        )
        assert resp.status_code == 200
        assert "account_id" in resp.json()


@pytest.mark.asyncio
async def test_crm_update_and_ticket():
    transport = ASGITransport(app=crm_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create = await client.post(
            "/tools/create_account",
            json={"company": "Co", "plan": "Pro"},
        )
        account_id = create.json()["account_id"]
        update = await client.post(
            "/tools/update_account",
            json={"account_id": account_id, "fields": {"plan": "Enterprise"}},
        )
        assert update.json()["status"] == "updated"
        ticket = await client.post(
            "/tools/create_ticket",
            json={"account_id": account_id, "subject": "Help"},
        )
        assert "ticket_id" in ticket.json()


@pytest.mark.asyncio
async def test_billing_subscription():
    transport = ASGITransport(app=billing_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/tools/get_subscription",
            json={"account_id": "acc-demo-001"},
        )
        assert resp.json()["plan"] == "Pro"


@pytest.mark.asyncio
async def test_diagnostics_run_and_report():
    transport = ASGITransport(app=diag_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        run = await client.post("/tools/run", json={"integration_id": "int-ok"})
        assert run.json()["status"] == "passed"
        report_id = run.json()["report_id"]
        report = await client.post("/tools/get_report", json={"report_id": report_id})
        assert report.json()["status"] in ("ok", "passed")
