#!/bin/bash
source ./venv/bin/activate
# gunicorn -b localhost:8000 --config gunicorn_config.py app:app
gunicorn -b localhost:8000 --worker-class=gevent --worker-connections=1000 --workers=3 app:app
