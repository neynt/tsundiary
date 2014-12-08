web: gunicorn tsundiary:app --workers $WEB_CONCURRENCY --worker-class gevent
upgrade: python migrate.py db upgrade
