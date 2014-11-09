#!/usr/bin/env bash
# Migrates the local database for testing purposes.
source venv/bin/activate
DEBUG=1 DATABASE_URL=postgres://tsundiary@localhost:5432/tsundiary python migrate.py db upgrade
