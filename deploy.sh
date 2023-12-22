#!/bin/sh
gunicorn --config gunicorn_config.py 'app:app'
