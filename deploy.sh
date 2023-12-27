#!/bin/bash
source ./venv/bin/activate
uwsgi --ini ./uwsgi.ini --enable-threads -H ./venv
