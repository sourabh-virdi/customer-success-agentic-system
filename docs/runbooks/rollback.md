# Rollback Runbook

## Trigger

- SLO breach detected (latency, error rate, availability)
- Canary deployment failure
- Critical security incident

## Steps

1. Identify failing component via `trace_id` in observability dashboard
2. Halt canary traffic routing (set weight to 0%)
3. Roll back ECS task definition to previous revision
4. Roll back AgentCore runtime config to last known good version
5. Activate safe mode on Supervisor if MCP is degraded
6. Verify SLO recovery within 15 minutes
7. Document incident and update runbooks
