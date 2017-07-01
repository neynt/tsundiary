source venv/bin/activate
DATABASE_URL=postgres://tsundiary@localhost:5432/tsundiary DEBUG=1 python migrate.py db migrate
