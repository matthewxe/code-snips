#!/bin/bash
 
python -m venv ./venv
pip install nodeenv
nodeenv -p
source ./venv/bin/activate
npm i --prefix ./static/npm/ bootstrap@5.3.2
npm install -g sass
sass ./static/scss/custom.scss ./static/css/bootstrap.css
pip install -r requirements.txt
 
