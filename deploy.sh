#!/bin/bash
source ./venv/bin/activate
gunicorn -b 127.0.0.1:5000 --config gunicorn_config.py 'app:app'
