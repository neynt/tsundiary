#!/bin/bash
source venv/bin/activate
[[ -f .env ]] && export $(cat .env | xargs)
python migrate.py db migrate
