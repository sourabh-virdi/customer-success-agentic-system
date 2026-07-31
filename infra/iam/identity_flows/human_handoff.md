# Human Handoff Identity Flow

1. Supervisor detects escalation need (safe mode, policy violation, user request).
2. Supervisor calls `crm.create_ticket` via MCP with session context.
3. Human agent authenticates via corporate SSO.
4. System attaches `audit_id` linking:
   - Session transcript (redacted)
   - Memory snapshot
   - Trace ID chain
5. Human actions logged with SSO identity for regulatory audit.
