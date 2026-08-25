# Incident Response Runbook

## Triage (0–15 min)

1. Identify `trace_id` from alert or user report
2. Determine failing component: Supervisor, Leaf, MCP, Memory, or backend
3. Assess severity: P1 (data leak/outage), P2 (degraded), P3 (minor)

## Containment (15–60 min)

1. Activate circuit breakers or safe mode as needed
2. Block affected agent identities if security incident
3. Preserve audit logs and traces (do not delete)

## Remediation

1. Roll back or patch failing component
2. Re-run evaluation harness and e2e tests
3. Verify dashboards return to normal

## Postmortem

1. Root cause analysis within 48 hours
2. Action items assigned with owners
3. Update security checklist and runbooks
4. Schedule regression tests for similar failures
