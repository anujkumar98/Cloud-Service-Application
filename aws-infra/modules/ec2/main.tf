resource "random_uuid" "uuid" {}
resource "aws_key_pair" "ec2key" {
  key_name   = "ssh_key-${random_uuid.uuid.result}"
  public_key = file(var.public_key_path)
}

resource "aws_instance" "aws_ec2_csye6225" {
  ami                  = var.ami_id
  instance_type        = var.instance_type
  subnet_id            = var.subnet_id
  key_name             = aws_key_pair.ec2key.key_name
  iam_instance_profile = var.access_policy_attachemet_name

  user_data = <<-EOF
    #!/bin/bash
    cd /tmp/webapp
    touch .env
    sudo chown ec2-user:ec2-user .env
    {
      echo "HOST=${var.rds_endpoint}"
      echo "USERNAME=${var.rds_username}" 
      echo "PASSWORD=${var.rds_password}"
      echo "SCHEMA_NAME=csye6225"
      echo "S3_Bucket_Name=${var.s3_bucket_name}"
    } >> .env
    sudo systemctl daemon-reload
    sudo systemctl enable fastapi_service
    sudo systemctl start fastapi_service
    EOF
  connection {
    type        = "ssh"
    user        = "ec2-user"
    private_key = file("${aws_key_pair.example_keypair.key_name}.pem")
  }
  ebs_block_device {
    device_name           = "/dev/xvda"
    volume_type           = "gp2"
    delete_on_termination = true
  }
  vpc_security_group_ids = var.security_group_id
  root_block_device {
    volume_size = 50
    volume_type = "gp2"
  }
  # Disable protection against accidental termination
  disable_api_termination = true
  tags = {
    Name = "ec2-csye6225"
  }
}

