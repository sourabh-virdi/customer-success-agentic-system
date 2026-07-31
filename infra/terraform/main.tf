terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "iam" {
  source      = "./modules/iam"
  environment = var.environment
}

module "mcp" {
  source      = "./modules/mcp"
  environment = var.environment
  vpc_id      = module.networking.vpc_id
}

module "agents" {
  source      = "./modules/agents"
  environment = var.environment
}

module "observability" {
  source      = "./modules/observability"
  environment = var.environment
}

module "secrets" {
  source      = "./modules/secrets"
  environment = var.environment
}

module "networking" {
  source      = "./modules/networking"
  environment = var.environment
}
