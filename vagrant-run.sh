#/usr/bin/env bash
source venv/bin/activate
DEBUG=1 DATABASE_URL=postgres://tsundiary:baka@localhost:5432/tsundiary python -i runserver.py
