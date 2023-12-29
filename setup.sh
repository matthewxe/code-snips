#!/bin/bash
 
python -m venv ./venv
source ./venv/bin/activate
# pip install --upgrade pip
pip install nodeenv
nodeenv -p
npm i --prefix ./static/npm/ bootstrap@5.3.2 ace-builds
npm install -g sass
sass ./static/scss/custom.scss ./static/css/bootstrap.css
pip install -r requirements.txt
 
export SECRET_KEY=$(python3 -c "from secrets import token_urlsafe; print(token_urlsafe())")
export SECURITY_PASSWORD_SALT=$(python3 -c "from secrets import SystemRandom; print(SystemRandom().getrandbits(128))")
