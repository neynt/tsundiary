web: gunicorn tsundiary:app --workers $WEB_CONCURRENCY
upgrade: python migrate.py db upgrade
