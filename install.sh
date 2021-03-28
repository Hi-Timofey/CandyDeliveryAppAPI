#/usr/bin/env bash
activate () {
    . flask_env/bin/activate
}

# Installing python3 
sudo apt install python3 python-pip
# Installing virtual env
python3 -m pip install virtualenv
# Creating env and load into
python3 -m virtualenv .flask_env

# Activating venv
activate

# Installing requirements.txt
python3 -m pip install -r requirements.txt
