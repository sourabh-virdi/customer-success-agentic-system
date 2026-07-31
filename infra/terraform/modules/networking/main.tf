variable "environment" { type = string }

output "vpc_id" {
  value = "vpc-placeholder-${var.environment}"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = { Name = "cs-agent-${var.environment}" }
}
