# Memory API

AgentCore Memory CRUD stubs with PII redaction and governance.

```bash
export PYTHONPATH=agents/shared:memory/api
uvicorn memory.api.main:app --reload --port 8001
```

Schemas: `memory/schemas/`
