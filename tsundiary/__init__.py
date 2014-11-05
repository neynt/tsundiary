# encoding=utf-8
import os
import random
from urlparse import urlparse, urlunparse
from datetime import datetime, date, timedelta
from flask import Flask, redirect, session, request, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask_sslify import SSLify

#################
# Initialization

# Lovable diary prompts!
#insults = [
#"moron", "idiot", "fool"
#]

# The ideal tsundere greeting is cold and hostile while betraying a
# lingering sense of affection. Constantly search for it.

# Set up Flask app
app = Flask(__name__)

# Database URL, or sqlite in-memory database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
# Secret key (for sessions/cookies)
app.secret_key = os.environ.get('SECRET_KEY') or 'yolodesu'

# Automatically redirect to https
sslify = SSLify(app)

# Sessions last for 100 years
app.permanent_session_lifetime = timedelta(days=36500)

# Import the rest of the tsundiary stuff
from tsundiary.views import *
from tsundiary.models import User, db
from tsundiary.utils import their_date

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

############
# App funcs

@app.before_request
def before_request():
    # Redirect non-www.com requests to www.com
    urlparts = urlparse(request.url)
    if urlparts.netloc in {
        'tsundiary.tk',
        'www.tsundiary.tk',
        'tsundiary.com'
    }:
        urlparts_list = list(urlparts)
        urlparts_list[1] = 'www.tsundiary.com'
        return redirect(urlunparse(urlparts_list), code=301)

    # Load user information
    g.user = User.query.filter_by(sid=session.get('user_sid')).first()

    if g.user and 'timezone' in request.cookies:
        g.timezone = int(request.cookies['timezone'])
        if g.timezone != g.user.timezone:
            g.user.timezone = g.timezone
            db.session.commit()
    elif g.user:
        g.timezone = g.user.timezone or 0
    else:
        g.timezone = 0

    g.date = their_date()
    if g.user:
        g.theme = g.user.theme
        g.color = g.user.color
    else:
        g.theme = None
        g.color = None
