.PHONY: install lint test run-mcp run-memory run-mocks run-agents eval

PYTHONPATH=agents/shared:mcp/src:memory/api:evaluations:mocks

install:
	pip install -r requirements.txt

lint:
	ruff check agents mcp memory mocks evaluations tests

test:
	PYTHONPATH=agents/shared:mcp/src:memory/api:evaluations:mocks:infra/agentcore_configs python -m pytest tests/ -v --cov --cov-fail-under=85

run-mcp:
	PYTHONPATH=agents/shared:mcp/src uvicorn cs_mcp.main:app --reload --port 8000

run-memory:
	PYTHONPATH=agents/shared:memory/api uvicorn memory.api.main:app --reload --port 8001

run-mocks:
	PYTHONPATH=mocks uvicorn mocks.crm.main:app --port 8010 &
	PYTHONPATH=mocks uvicorn mocks.billing.main:app --port 8011 &
	PYTHONPATH=mocks uvicorn mocks.diagnostics.main:app --port 8012

eval:
	PYTHONPATH=$(PYTHONPATH) python evaluations/harness/runner.py
