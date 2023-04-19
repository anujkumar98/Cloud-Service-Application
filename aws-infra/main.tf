provider "aws" {
  region  = var.aws_default_region
  profile = var.aws_default_profile
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.46"
    }
  }
}
resource "random_uuid" "uuid" {}
module "vpc" {
  source         = "./modules/vpc"
  vpc_cidr_value = var.vpc_cidr_value
}

module "subnet" {
  source          = "./modules/subnets"
  vpc_instance_id = module.vpc.vpc_instance_id
  vpc_cidr_value  = var.vpc_cidr_value
}
module "route_table" {
  source            = "./modules/route_tables"
  vpc_instance_id   = module.vpc.vpc_instance_id
  igw_id            = module.vpc.internet_gateway_id
  public_subnet_id  = module.subnet.public_subnet_id
  private_subnet_id = module.subnet.private_subnet_id
}

module "security_group" {
  source = "./modules/security_group"
  vpc_id = module.vpc.vpc_instance_id
}

module "s3" {
  source              = "./modules/s3"
  aws_default_profile = var.aws_default_profile
}

module "rds" {
  source              = "./modules/rds"
  private_subnet_id   = module.subnet.private_subnet_id
  security_group_id   = module.security_group.database_security_group_id
  private_subnet_name = module.subnet.private_subnet_name
  uuid_generated      = random_uuid.uuid.result
  rds_username        = var.rds_username
  rds_password        = var.rds_password
}

module "iam_roles" {
  source = "./modules/iam_roles"
  s3_arn = module.s3.aws_s3_arn
}

module "route53" {
  source     = "./modules/route53"
  lb_dns     = module.load_balancer.load_balancer_public_ip
  lb_zone_id = module.load_balancer.lb_zone_id
  webapp_url = var.webapp_url
}
module "load_balancer" {
  source            = "./modules/load_balancer"
  security_group_id = [module.security_group.load_balancer_security_group]
  lb_subnets        = module.subnet.public_subnet_id
  vpc_id            = module.vpc.vpc_instance_id
  webapp_url        = var.webapp_url
}

module "autoscaling_group" {
  source                        = "./modules/autoscaling_group"
  ami_id                        = var.ami_id
  security_group_id             = [module.security_group.application_security_group_id]
  subnet_id                     = module.subnet.public_subnet_id
  access_policy_attachemet_name = module.iam_roles.access_policy_attachemet_name
  rds_endpoint                  = module.rds.rds_endpoint
  rds_username                  = var.rds_username
  rds_password                  = var.rds_password
  s3_bucket_name                = module.s3.aws_bucket_name
  lb_target_group_arn           = module.load_balancer.lb_target_group_arn
}
