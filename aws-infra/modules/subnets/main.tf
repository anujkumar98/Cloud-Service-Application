data "aws_availability_zones" "available" {
  state = "available"
}
locals {
  num_subnets                = min(length(data.aws_availability_zones.available.names), 3)
  public_subnets_cidr_block  = cidrsubnet(var.vpc_cidr_value, 4, 1) # e.g. "10.0.1.0/20"
  private_subnets_cidr_block = cidrsubnet(var.vpc_cidr_value, 4, 2) # e.g. "10.0.2.0/20"
}
resource "aws_subnet" "public_subnet" {
  count                   = local.num_subnets
  vpc_id                  = var.vpc_instance_id
  cidr_block              = cidrsubnet(local.public_subnets_cidr_block, 8, count.index)
  map_public_ip_on_launch = true
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  tags = {
    Name = format("public_subnet-%s", count.index)
  }
}

resource "aws_subnet" "private_subnet" {
  count             = local.num_subnets
  vpc_id            = var.vpc_instance_id
  cidr_block        = cidrsubnet(local.private_subnets_cidr_block, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = {
    Name = format("private_subnet-%s", count.index)
  }
}