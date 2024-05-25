#!/bin/bash

source venv/bin/activate
# pip3 install -r ./requirements.txt
sass --watch ./static/scss/custom.scss ./static/css/bootstrap.css &
flask --app app.py --debug run --port 8000 
