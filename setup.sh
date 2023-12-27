#!/bin/sh
 
python -m venv ./venv
sass ./static/scss/custom.scss ./static/css/bootstrap.css
source ./venv/bin/activate
pip install -r requirements.txt
 
