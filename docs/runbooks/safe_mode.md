# Safe Mode Runbook

## When to Activate

- MCP server unavailable or circuit breakers open
- Tool error rate > 5% sustained for 5 minutes
- Identity/token exchange failures

## Behavior

Supervisor returns human escalation message instead of routing to leaf agents:

> Our automated systems are temporarily unavailable. A human agent will assist you shortly.

## Steps

1. Confirm MCP health: `curl http://localhost:8000/health`
2. Check circuit breaker status in MCP metrics
3. If MCP recoverable, restart service and verify `/tools` endpoint
4. If prolonged outage, route all traffic to human support queue
5. Disable safe mode only after integration tests pass
