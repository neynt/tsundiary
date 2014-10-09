# encoding=utf-8
import os
import random
from urlparse import urlparse, urlunparse
from datetime import datetime, date, timedelta
from flask import Flask, redirect, session, request, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

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
    g.timezone = int(request.cookies.get('timezone') or '0')
    g.date = their_date()
    if g.user:
        g.theme = g.user.theme
    else:
        g.theme = None
