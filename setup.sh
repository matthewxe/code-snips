#!/bin/sh
 
python -m venv ./venv
npm i --prefix ./static/npm/ bootstrap@5.3.2
sass ./static/scss/custom.scss ./static/css/bootstrap.css
source ./venv/bin/activate
pip install -r requirements.txt
 
