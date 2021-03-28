#/usr/bin/env bash

# Installing virtual env
python3 -m pip install virtualenv
# Creating env and load into
python3 -m virtualenv .flask_env
source .flask_env/bin/activate

# Installing requirements.txt
python3 -m pip install -r requirements.txt
