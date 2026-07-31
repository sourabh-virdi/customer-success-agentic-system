variable "environment" { type = string }
variable "vpc_id" { type = string }

output "service_name" {
  value = "cs-mcp-${var.environment}"
}

resource "aws_ecs_service" "mcp" {
  name            = "cs-mcp-${var.environment}"
  cluster         = "cs-agent-${var.environment}"
  task_definition = "cs-mcp-task"
  desired_count   = 2
}
