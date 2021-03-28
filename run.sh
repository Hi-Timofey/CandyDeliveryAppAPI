#/usr/bin/env bash
activate () {
    . .flask_env/bin/activate
}


export API_CONFIG=config.cfg
activate
python3 -m pytest tests.py
python3 app.py
