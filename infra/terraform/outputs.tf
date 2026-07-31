output "mcp_service_name" {
  value = module.mcp.service_name
}

output "agent_runtime_arns" {
  value = module.agents.runtime_arns
}

output "vpc_id" {
  value = module.networking.vpc_id
}
