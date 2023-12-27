#!/bin/bash
source ./venv/bin/activate
gunicorn --config gunicorn_config.py app:app
# gunicorn --worker-class=gevent --worker-connections=1000 --workers=3 app:app
