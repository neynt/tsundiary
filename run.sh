#!/bin/bash
source venv/bin/activate
[[ -f .env ]] && export $(cat .env | xargs)
#python -i runserver.py
exec gunicorn tsundiary:app --workers $WEB_CONCURRENCY --worker-class gevent
