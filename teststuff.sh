#/usr/bin/env bash
# Runs the tsundiary server locally.
# Requires postgresql with a user called "tsundiary".
source venv/bin/activate
DEBUG=1 DATABASE_URL=postgres://tsundiary@localhost:5432/tsundiary python -i runserver.py
