# MCP Token Exchange Flow

1. Leaf agent receives task from Supervisor with `session_id` and `purpose`.
2. Agent calls `POST /auth/exchange` on MCP server:

```json
{
  "agent_identity": "leaf_b_diagnostics",
  "scope": "diagnostics:run",
  "session_id": "s-abc-123"
}
```

3. MCP validates agent identity against IAM mapping.
4. MCP issues scoped backend token bound to `session_id` (TTL: 10 minutes).
5. Agent uses token for subsequent `POST /call` requests.
6. MCP logs exchange in immutable audit log with `trace_id`.

See `agents/shared/examples/identity_exchange.py` for a runnable example.
