#!/bin/bash
 
python -m venv ./venv
source ./venv/bin/activate
pip install nodeenv
nodeenv -p
npm i --prefix ./static/npm/ bootstrap@5.3.2
npm install -g sass
sass ./static/scss/custom.scss ./static/css/bootstrap.css
pip install -r requirements.txt
 
