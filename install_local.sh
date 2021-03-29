#/usr/bin/env bash
activate () {
    . .flask_env/bin/activate
}

# Установка Docker
sudo apt -y update && sudo apt -y upgrade
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update && apt-cache policy docker-ce
sudo apt -y install docker-ce docker-compose

# Installing python3 
sudo apt install python3 python3-pip
# Installing virtual env
python3 -m pip install virtualenv
# Creating env and load into
python3 -m virtualenv .flask_env

# Activating venv
activate

# Installing requirements.txt
python3 -m pip install -r api/requirements.txt
