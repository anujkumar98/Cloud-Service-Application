variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "source_ami" {
  type    = string
  default = "ami-0dfcb1ef8550277af"
}

variable "ssh_username" {
  type    = string
  default = "ec2-user"
}

variable "subnet_id" {
  type    = string
  default = "subnet-068dab9951d2a234d"
}

variable "instance_type" {
  type = string
}

variable "ami_users" {
  type = list(string)
}

variable "ami_region" {
  type = list(string)
}
source "amazon-ebs" "my-ami" {
  region      = "${var.aws_region}"
  ami_name    = "csye_6225_my-ami-${formatdate("YYYY-MM-DD-hhmmss", timestamp())}"
  ami_regions = "${var.ami_region}"
  profile     = "dev"
  aws_polling {
    delay_seconds = 120
    max_attempts  = 50
  }
  source_ami_filter {
    filters = {
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["amazon"]
  }
  instance_type = "${var.instance_type}"
  source_ami    = "${var.source_ami}"
  ssh_username  = "${var.ssh_username}"
  subnet_id     = "${var.subnet_id}"
  ami_users     = "${var.ami_users}"
  launch_block_device_mappings {
    delete_on_termination = true
    device_name           = "/dev/xvda"
    volume_size           = 8
    volume_type           = "gp2"
  }
}
build {
  sources = ["amazon-ebs.my-ami"]
  provisioner "file" {
    source      = "dist/webapp.zip"
    destination = "/tmp/webapp.zip"
  }
  provisioner "shell" {
    script = "Scripts/installation.sh"
  }
  provisioner "shell" {
    script = "Scripts/webapp_setup.sh"
  }
  provisioner "shell" {
    script = "Scripts/cloudwatch_setup.sh"
  }
  post-processor "manifest" {
   output = "manifest.json"
   strip_path = true
  }
}

