resource "aws_vpc" "vpc" {
  cidr_block = var.vpc_cidr_value
  tags = {
    Name = "main_vpc"
  }
}
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id
  tags = {
    Name = "internet-gateway"
  }
}
