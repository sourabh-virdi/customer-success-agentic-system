variable "environment" { type = string }

resource "aws_iam_role" "supervisor" {
  name = "cs-supervisor-${var.environment}"
}

resource "aws_iam_role" "mcp_service" {
  name = "cs-mcp-service-${var.environment}"
}
