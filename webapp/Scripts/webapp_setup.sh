#!/bin/bash
export PATH="$PATH:/home/ec2-user/.local/bin"
source ~/.bashrc
cd /tmp
mkdir webapp
unzip webapp.zip -d webapp
cd webapp
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
#Service file
{
sudo echo [Unit]
sudo echo Description=Python Service
sudo echo After=multi-user.target
sudo echo [Service]
sudo echo Type=simple
sudo echo Restart=always
sudo echo ExecStart=/tmp/webapp/env/bin/python3 /tmp/webapp/main.py
sudo echo User=ec2-user
sudo echo WorkingDirectory=/tmp/webapp
sudo echo [Install]
sudo echo WantedBy=multi-user.target
} >> fastapi_service.service
sudo mv fastapi_service.service /etc/systemd/system/
sudo chown root:root /etc/systemd/system/fastapi_service.service
mkdir logs
touch cloudlogs.log
