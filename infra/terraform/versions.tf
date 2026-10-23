terraform {
  required_version = ">= 1.9, < 2.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.70"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "claims-intelligence"
      Environment = var.environment
      ManagedBy   = "terraform"
      CostOwner   = var.cost_owner
    }
  }
}
