terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.86.1"
    }
  }

  backend "s3" {} # set dynamically
}

provider "aws" {
  # these credentials do not allow access: for that role must be assumed
  access_key = var.aws_key_id
  secret_key = var.aws_secret_key
  region = var.aws_region

  assume_role {
    role_arn = var.aws_terraform_role_arn
    external_id = var.aws_assume_role_external_id
    duration = "1h"
    session_name = "PizzaRollerTerraformSession"
  }

  default_tags {
    tags = {
      application = "PizzaRollerBot"
      managed_by = "Terraform"
      repository = "https://github.com/Gtomika/pizza-roller-bot"
      owner = "Tamas Gaspar"
      environment = var.environment
    }
  }
}