#!/bin/sh
 
python -m venv ./venv
nodeenv -p
npm i --prefix ./static/npm/ bootstrap@5.3.2
npm install -g sass
sass ./static/scss/custom.scss ./static/css/bootstrap.css
source ./venv/bin/activate
pip install -r requirements.txt
 
