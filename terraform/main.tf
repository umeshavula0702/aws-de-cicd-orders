terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0, < 7.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "demo" {
  bucket = "de-cicd-tf-${data.aws_caller_identity.current.account_id}-${var.environment}"

  tags = {
    Project     = "AWS-DE-CICD"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
