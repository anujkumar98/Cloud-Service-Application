resource "aws_route_table" "public" {
  vpc_id = var.vpc_instance_id
  tags = {
    Name = "public_route_table"
  }
}
resource "aws_route_table" "private" {
  vpc_id = var.vpc_instance_id
  tags = {
    Name = "private_route_table"
  }
}

resource "aws_route_table_association" "public_rta" {
  count          = length(var.public_subnet_id)
  subnet_id      = var.public_subnet_id[count.index]
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private_rta" {
  count          = length(var.private_subnet_id)
  subnet_id      = var.private_subnet_id[count.index]
  route_table_id = aws_route_table.private.id
}

# Public Route to IGW
resource "aws_route" "public" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = var.igw_id
}
