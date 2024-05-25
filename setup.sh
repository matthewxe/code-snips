#!/bin/bash
 
python -m venv ./venv
source ./venv/bin/activate
# pip install --upgrade pip
pip install nodeenv
nodeenv -p
npm i --prefix ./static/npm/ bootstrap@4.3.2 ./static/npm ace-builds
npm install -g sass
sass ./static/scss/custom.scss ./static/css/bootstrap.css
pip install -r requirements.txt
 
