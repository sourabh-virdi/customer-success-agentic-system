variable "environment" { type = string }

resource "aws_secretsmanager_secret" "mcp_config" {
  name = "cs-mcp-config-${var.environment}"
}
