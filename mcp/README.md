# MCP Server

FastAPI MCP server with tool registry, auth exchange, policy hooks, and audit logging.

## Run locally

```bash
pip install -r requirements.txt
export PYTHONPATH=agents/shared:mcp/src
uvicorn cs_mcp.main:app --reload --port 8000
```

## Endpoints

- `POST /tools/register` — register tools
- `GET /tools` — list tools
- `POST /call` — invoke tool
- `POST /auth/exchange` — token exchange
- `GET /metrics` — Prometheus metrics
