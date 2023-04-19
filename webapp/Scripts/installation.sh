#!/bin/bash
sudo yum update -y
sudo yum upgrade -y
export PATH="$PATH:/home/ec2-user/.local/bin"
source ~/.bashrc
pip3 install --upgrade pip
pip3 install --user virtualenv
sudo amazon-linux-extras install epel -y
sudo yum install mysql -y