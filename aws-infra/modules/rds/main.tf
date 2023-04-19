resource "aws_db_parameter_group" "rds_parameter_group_csye6225" {
  name   = "parameter-group-database-${var.uuid_generated}"
  family = "mysql8.0"
  tags = {
    Name : "rds_parameter_group_csye6225"
  }
}

resource "aws_db_subnet_group" "private_subnet_group" {
  name       = "example-subnet-group-${var.uuid_generated}"
  subnet_ids = var.private_subnet_id

  tags = {
    Name = "private-subnet-group"
  }
}

data "aws_caller_identity" "current" {}

resource "aws_kms_key" "rds_kms_key" {
  description             = "KMS key for RDS instance"
  deletion_window_in_days = 10
  enable_key_rotation = true
    policy = jsonencode({
    "Id": "key-consolepolicy-3",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
            },
            "Action":"kms:*",
            "Resource": "*"
        },
        {
            "Sid": "Allow use of the key",
            "Effect": "Allow",
            "Principal": {
                "Service" = "rds.amazonaws.com"
            },
            "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
                "kms:DescribeKey"
            ],
            "Resource": "*"
        },
        {
            "Sid": "Allow attachment of persistent resources",
            "Effect": "Allow",
            "Principal": {
               "Service" = "rds.amazonaws.com"
            },
            "Action": [
                "kms:CreateGrant",
                "kms:ListGrants",
                "kms:RevokeGrant"
            ],
            "Resource": "*",
            "Condition": {
                "Bool": {
                    "kms:GrantIsForAWSResource": "true"
                }
            }
        }
    ]
})
}

resource "aws_db_instance" "csye6225" {
  engine                 = "mysql"
  allocated_storage      = 10
  engine_version         = "8.0"
  instance_class         = "db.t3.micro"
  db_name                = "csye6225"
  username               = var.rds_username
  password               = var.rds_password
  publicly_accessible    = false
  parameter_group_name   = aws_db_parameter_group.rds_parameter_group_csye6225.name
  db_subnet_group_name   = aws_db_subnet_group.private_subnet_group.name
  vpc_security_group_ids = [var.security_group_id]
  skip_final_snapshot    = true
  identifier_prefix      = "csye6225-db-instance-"
  storage_encrypted      = true
  kms_key_id             = aws_kms_key.rds_kms_key.arn
  tags = {
    Name = "csye6225-db-instance"
  }
}


