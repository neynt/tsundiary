import os
import random
from datetime import datetime, date, timedelta
import calendar
from flask import render_template, send_from_directory, redirect, session, request, g, flash
from collections import defaultdict
from tsundiary import app
from tsundiary.models import User, Post, db
from tsundiary.prompts import PROMPTS
from tsundiary.utils import *

@app.errorhandler(404)
def page_not_found(e=None):
    return render_template('404.html'), 404

# Route static files
static_file_dir = os.path.dirname(os.path.realpath(__file__)) + '/static'
@app.route('/static/<path:filename>')
def static_file(filename):
    return send_from_directory(static_file_dir, filename)
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(static_file_dir, "favicon.ico")

# Raw dump for data liberation.
@app.route('/raw_dump')
def raw_dump():
    if not g.user:
        return "Login kudasai."
    return render_template('raw_dump.html',
                           posts=g.user.posts)

# Updating content
@app.route('/confess', methods=['POST'])
def confess():
    content = request.form.get('content').strip()
    try:
        cur_date = date_from_stamp(request.form.get('cur_date'))
    except:
        return "w-what are you trying to do to me???"
    if valid_date(cur_date):
        return_message = ""

        if 0 < len(content) <= 20000:
            new_post = Post(g.user.sid, content, cur_date)
            db.session.merge(new_post)
            combo = 1
            return_message = "saved!"
        elif len(content) == 0:
            p = g.user.posts.filter_by(posted_date = cur_date)
            if p:
                p.delete()
            combo = 0
            return_message = "deleted!"
        else:
            return_message = "onii-chan, it's too big! you're gonna split me in half!"

        db.session.commit()

        # Update number of entries
        g.user.num_entries = g.user.posts.count()
        # Update latest post date
        g.user.latest_post_date = cur_date
        # Update combo
        cd = cur_date - timedelta(days = 1)
        while g.user.posts.filter_by(posted_date = cd).first():
            combo += 1
            cd -= timedelta(days = 1)
        g.user.combo = combo

        db.session.commit()

        return return_message
    else:
        return "... you want to go on a DATE with me!?"

# Login attempts
@app.route('/attempt_login', methods=['POST'])
def attempt_login():
    u = request.form['username']
    p = request.form['password']
    user = User.query.filter_by(sid = uidify(u)).first()
    if user and user.verify_password(p):
        session['user_sid'] = uidify(u)
        session.permanent = True
        return redirect('/')
        #return "Oh... welcome back, %s-sama." % u
    elif "'" in u or "'" in p:
        flash('H-honto baka!')
        #return "H-honto baka! Did you really think that would work?!"
    flash("I don't recognize you, sorry.")
    return redirect('/')
    #return "I don't recognize you, sorry."

# Logout
@app.route('/logout')
def logout():
    if g.user and request.args.get('user') == g.user.sid:
        session.pop('user_sid', None)
    return redirect('/')

def render_diary(author, posts, title="Recent entries"):
    hidden_day = calc_hidden_day(author)

    # Generate months/years that the user actually posted something
    # e.g. 2014: Jan Feb Mar May
    dates = defaultdict(set)
    written_dates = db.session.query(Post.posted_date).filter(Post.user == author).all()
    for r in written_dates:
        d = r[0]
        dates[d.year].add(d.month)

    return render_template(
            "user.html",
            author = author,
            posts = posts,
            hidden_day = hidden_day,
            dates = dates,
            month_name = calendar.month_name,
            title = title
            )

# For "scroll-down" content loading
@app.route('/+<author_sid>/<datestamp>')
def fetch_next_post(author_sid, datestamp):
    author = User.query.filter_by(sid = author_sid).first()
    if author:
        y, m, d = map(int, datestamp.split('-'))
        hidden_day = calc_hidden_day(author)
        cur_date = date(y, m, d)
        post = (author.posts
               .filter(Post.posted_date < cur_date)
               .order_by(Post.posted_date.desc())
               .first())
        if post:
            return render_template('entry.html', p=post, hidden_day=hidden_day)
        else:
            return 'no more'
    else:
        return page_not_found()

# A certain selection of dates from a user's diary.
@app.route('/~<author_sid>/<year>/<month>')
def diary(author_sid, year, month):
    author = User.query.filter_by(sid = uidify(author_sid)).first()
    if author:
        yyyy, mm = int(year), int(month)
        min_date = date(yyyy, mm, 1)
        max_date = date(yyyy, mm, calendar.monthrange(yyyy, mm)[1])
        posts = author.posts\
            .filter(Post.posted_date >= min_date)\
            .filter(Post.posted_date <= max_date)\
            .order_by(Post.posted_date.asc())\
            .all()
        return render_diary(author, posts, min_date.strftime('%B %Y'))
    else:
        return page_not_found()

# Custom commands
@app.route('/~<author_sid>/<command>')
def diary_special(author_sid, command):
    author = User.query.filter_by(sid = uidify(author_sid)).first()
    if author:
        if command == 'all':
            posts = author.posts.order_by(Post.posted_date.desc()).all()
            return render_diary(author, posts, "All entries")
        else:
            return page_not_found()
    else:
        return page_not_found()

# Last secret_days + 1 entries of a user's diary.
@app.route('/~<author_sid>')
def diary_preview(author_sid):
    # Dict of year: [list months]
    author = User.query.filter_by(sid = uidify(author_sid)).first()
    if author:
        posts = (author.posts.order_by(Post.posted_date.desc())
                 .limit(max(5, author.secret_days+3)).all())
        return render_diary(author, posts)
    else:
        return page_not_found()

# User registration form.
@app.route('/register')
def register():
    return render_template('register.html')

# registration action
@app.route('/register', methods=['POST'])
def register_action():
    invite_key = request.form.get('invite_key')
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email') or None

    # check if we already have too many users
    if User.query.count() > 400 and invite_key != 'koi dorobou':
        flash("Actually, we're out of spots for registrations. Sorry!")
    elif len(username) < 2:
        flash("Please enter a username at least 2 characters long.")
    elif len(password) < 3:
        flash("Please enter a password at least 3 characters long.")
    elif User.query.filter_by(sid=uidify(username)).first():
        flash("We already have someone with that name.")
    else:
        new_user = User(username, password)
        new_user.email = email
        new_user.invite_key = invite_key
        db.session.add(new_user)
        db.session.commit()
        session['user_sid'] = new_user.sid
        session.permanent = True
        return redirect('/')
    return redirect('/register')

# List of users.
@app.route('/userlist')
def userlist():
    all_users = (User.query.order_by(User.num_entries.desc())
            .filter(User.publicity >= 2)
            .filter(User.num_entries >= 2)
            .all())
    return render_template('userlist.html', all_users=all_users)

# List of users (sorted by latest new post)
@app.route('/userlist/latest')
def userlist_latest():
    all_users = (User.query.order_by(User.latest_post_date.desc())
            .order_by(User.num_entries.desc())
            .filter(User.publicity >= 2)
            .filter(User.num_entries >= 2)
            .filter(User.latest_post_date >= date.today() - timedelta(days=1))
            .all())
    return render_template('userlist.html', all_users=all_users)

# List of users (including throwaways).
@app.route('/userlist/all')
def userlist_all():
    all_users = (User.query.order_by(User.latest_post_date.desc())
            .order_by(User.num_entries.desc())
            .filter(User.publicity >= 2)
            .filter(User.num_entries >= 1)
            .all())
    return render_template('userlist.html', all_users=all_users)

@app.route('/h-hello...')
def who_am_i():
    return render_template('what-is-this.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/markdown')
def markdown_guide():
    return render_template('markdown-guide.html')

@app.route('/settings')
def edit_settings():
    if not g.user:
        return page_not_found()

    private = (g.user.publicity == 0)
    return render_template('settings.html', private=private)

@app.route('/change_setting', methods=['POST'])
def edit_settings_action():
    if not g.user:
        return page_not_found()

    setting_name = request.form.get('setting_name')
    setting_value = request.form.get('setting_value')

    if setting_name == 'private':
        # True
        if int(setting_value):
            g.user.publicity = 0
        else:
            g.user.publicity = 2
        db.session.commit()
        return 'saved!'
    elif setting_name == 'secret_days':
        if setting_value == 'Hidden':
            g.user.publicity = 1
        elif setting_value == 'Forever':
            g.user.publicity = 0
        else:
            g.user.publicity = 2
            g.user.secret_days = int(setting_value)
        db.session.commit()
        return 'saved!'
    elif setting_name == 'theme':
        g.user.theme = setting_value
        db.session.commit()
        return 'refresh to see theme'
    else:
        return 'error'
    return 'Jim messed up'

@app.route('/change_password', methods=['POST'])
def change_password():
    if not g.user:
        return page_not_found()

    old_pass = request.form.get('old_pass')
    new_pass = request.form.get('new_pass')

    if len(new_pass) < 3:
        return 'Please enter a new password at least 3 characters long.'

    if g.user.verify_password(old_pass):
        g.user.set_password(new_pass)
        db.session.commit()
        return 'password changed!'
    else:
        return 'wrong old password'

# Google webmaster verification
google = os.environ.get('GOOGLE_WEBMASTER')
if google:
    @app.route('/' + google)
    def submit_to_botnet():
        return "google-site-verification: " + google

# Index/home!
@app.route('/', methods=['GET', 'POST'])
def index():
    # handle logouts
    submit_action = request.form.get('action')
    if submit_action == 'logout':
        return logout()

    if g.user:
        current_post = g.user.posts.filter_by(posted_date = g.date).first()
        current_content = current_post.content if current_post else ""
        prompt = random.choice(PROMPTS) % g.user.name

        old_posts = []
        deltas = [(1, "yesterday"), (7, "one week ago"), (30, "30 days ago"),
                  (90, "90 days ago"), (365, "365 days ago")]
        for delta, delta_name in deltas:
            day = g.date - timedelta(days=delta)
            print("checking", day)
            p = g.user.posts.filter_by(posted_date=day).first()
            if p:
                old_posts.append((delta_name, p))

        print(old_posts)

        return render_template(
                'write.html',
                old_posts = old_posts,
                prompt = prompt,
                current_content = current_content)
    else:
        return render_template('front.html')
