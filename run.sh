export API_CONFIG=config_tests.cfg
source venv/bin/activate
python3 -m pytest tests.py
python3 app.py
