#/usr/bin/env bash
source venv/bin/activate
DEBUG=1 DATABASE_URL=sqlite:// python tests.py
