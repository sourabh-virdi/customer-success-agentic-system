# Human Handoff Runbook

## Escalation Triggers

- User explicitly requests human agent
- Safe mode active
- Policy violation or high-risk retention case
- Repeated failed tool calls

## Procedure

1. Supervisor creates ticket via `crm.create_ticket` MCP tool
2. Attach `audit_id` from MCP audit log
3. Export redacted session transcript from Memory API
4. Human agent authenticates via corporate SSO
5. Link SSO identity to `audit_id` for compliance trail
6. Human resolves case and logs disposition
7. Update session memory with resolution summary (redacted)
