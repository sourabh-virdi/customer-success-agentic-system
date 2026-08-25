# Deploy Runbook

## Prerequisites

- AWS credentials configured
- Terraform >= 1.5
- Docker installed

## Steps

1. Run `terraform -chdir=infra/terraform plan`
2. Apply infrastructure: `terraform -chdir=infra/terraform apply`
3. Build MCP image: `docker build -f mcp/Dockerfile -t cs-mcp:latest .`
4. Push to ECR and update ECS service
5. Deploy agent harnesses via AgentCore runtime configs in `infra/agentcore_configs/`
6. Register gateway tools: `python infra/agentcore_configs/export_gateway_tools.py`
7. Verify health endpoints and run e2e tests

## Verification

- `GET /health` on MCP, Memory, and agents returns 200
- Evaluation harness passes thresholds
- Dashboards show telemetry in CloudWatch/X-Ray
