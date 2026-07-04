# Customer Success Agent System

Production-ready multi-agent system using Amazon Bedrock AgentCore and an MCP server to coordinate a Supervisor agent and three Leaf agents (Onboarding, Diagnostics, Retention).

## Architecture

See [docs/architecture.md](docs/architecture.md) for diagrams and component overview.

## Quickstart

```bash
cp .env.example .env
pip install -r requirements.txt
make test
docker compose up
```

## Services

| Service | Port | Command |
|---------|------|---------|
| MCP Server | 8000 | `make run-mcp` |
| Memory API | 8001 | `make run-memory` |
| Mock CRM | 8010 | see mocks/README.md |
| Supervisor | 8020 | see agents/supervisor/README.md |

## Project Structure

- `mcp/` — MCP OpenAPI spec and FastAPI server
- `agents/` — Supervisor and Leaf agent harnesses
- `memory/` — JSON schemas and CRUD API
- `mocks/` — CRM, Billing, Diagnostics mocks
- `infra/` — Terraform, IAM, observability, AgentCore configs
- `evaluations/` — Synthetic scenarios and evaluation harness
- `tests/` — Unit, integration, e2e, safety tests
- `docs/` — Runbooks, security checklist, blog posts

## Documentation

- [Security Checklist](docs/security_checklist.md)
- [Runbooks](docs/runbooks/)
- [Technical Blog](docs/blog/)
