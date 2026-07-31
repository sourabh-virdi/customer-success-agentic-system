# Agent Startup Identity Flow

1. Agent pod starts with IAM role (e.g., `leaf_b_role`).
2. Agent calls AgentCore Identity `POST /identity/token` with `agent_id` and role ARN.
3. Identity issues short-lived runtime token (5–15 minutes).
4. Agent stores token in memory; refreshes before expiry.

## Environment variables

- `AGENT_IDENTITY` — unique agent identifier
- `AWS_REGION` — deployment region
- `AGENTCORE_MEMORY_ID` — memory store binding
