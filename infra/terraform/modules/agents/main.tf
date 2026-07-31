variable "environment" { type = string }

output "runtime_arns" {
  value = {
    supervisor = "arn:aws:bedrock-agentcore:${var.environment}:runtime/supervisor"
    leaf_a     = "arn:aws:bedrock-agentcore:${var.environment}:runtime/leaf_a"
    leaf_b     = "arn:aws:bedrock-agentcore:${var.environment}:runtime/leaf_b"
    leaf_c     = "arn:aws:bedrock-agentcore:${var.environment}:runtime/leaf_c"
  }
}
