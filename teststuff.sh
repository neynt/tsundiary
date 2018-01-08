#!/bin/bash
source venv/bin/activate
SECRET_KEY="cake" DEBUG=1 DATABASE_URL=postgres://tsundiary@localhost:5432/tsundiary python -i runserver.py
