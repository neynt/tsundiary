import os
import random
import calendar
import json
from collections import defaultdict
from datetime import datetime, date, timedelta

from flask import render_template, send_from_directory, redirect, session, request, g, flash

from tsundiary import app
from tsundiary.models import User, Post, db
from tsundiary.prompts import PROMPTS

@app.errorhandler(404)
def page_not_found(e=None):
    return render_template('404.html'), 404

# Raw dump for data liberation.
@app.route('/raw_dump')
def raw_dump():
    if not g.user:
        return "Login kudasai."
    return render_template('raw_dump.html',
                           posts=g.user.posts)

from tsundiary.views.confess import confess
from tsundiary.views.diary import *
from tsundiary.views.fetch_next_post import *
from tsundiary.views.index import *
from tsundiary.views.login import *
from tsundiary.views.logout import *
from tsundiary.views.register import *
from tsundiary.views.settings import *
from tsundiary.views.stalk import *
from tsundiary.views.static_pages import *
from tsundiary.views.theme_color import *
from tsundiary.views.userlist import *
from tsundiary.views.api import *
import tsundiary.views.hide_post
