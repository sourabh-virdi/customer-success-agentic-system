# Security Checklist

## Pre-Production

- [ ] IAM least privilege verified for all agent roles (`infra/iam/`)
- [ ] Secrets stored in vault with automatic rotation enabled
- [ ] PII redaction unit and e2e tests passing
- [ ] TLS enabled for all external endpoints
- [ ] Mutual TLS configured for agent ↔ MCP communication
- [ ] Audit trail immutable and exportable
- [ ] Penetration test scheduled with remediation plan
- [ ] Data residency configuration per tenant documented
- [ ] Consent management enforced for profile memory writes
- [ ] Forget/delete API tested for GDPR/CCPA compliance
- [ ] Prompt injection safety tests passing
- [ ] Rate limiting and circuit breakers configured
- [ ] Dashboards and SLO alerts deployed (`infra/observability/`)

## Ongoing

- [ ] Daily evaluation harness run
- [ ] Human rater sampling (0.5–1% sessions)
- [ ] Credential rotation audit monthly
- [ ] Security dashboard review weekly
