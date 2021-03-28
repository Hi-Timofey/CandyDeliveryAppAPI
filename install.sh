#/usr/bin/env bash

# Installing virtual env
python3 -m pip install virtualenv

# Creating env
python3 -m virtualenv .flask_env

# Installing requirements.txt
python3 -m pip install -r requirements.txt
