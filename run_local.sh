#/bin/sh
activate () {
    . .flask_env/bin/activate
}


export API_CONFIG=config.cfg
activate
python3 -m pytest api/tests.py
python3 api/app.py
