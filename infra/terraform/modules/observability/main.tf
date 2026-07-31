variable "environment" { type = string }

resource "aws_cloudwatch_log_group" "agents" {
  name              = "/cs-agent/${var.environment}"
  retention_in_days = 90
}

resource "aws_xray_group" "agents" {
  group_name        = "cs-agent-${var.environment}"
  filter_expression = "service(\"cs-agent-system\")"
}
