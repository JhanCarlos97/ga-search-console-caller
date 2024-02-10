terraform {
  backend "s3" {
    key         = "ga-analytics-service/terraform.tfstate"
    region      = "us-east-1"
  }
}
provider "aws" {
  region = "us-east-1"
}