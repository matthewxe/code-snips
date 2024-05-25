#!/bin/bash
source ./venv/bin/activate
gunicorn -b localhost:8000 --config gunicorn_config.py 'app:app'
