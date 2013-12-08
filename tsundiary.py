# encoding=utf-8
import os
import random
from datetime import datetime, date, timedelta
from flask import Flask, Markup, render_template, send_from_directory, redirect, session, request, g
from flask.ext.sqlalchemy import SQLAlchemy
import uuid
import hashlib
from markdown import markdown
import bleach

########################
# Initialization vectors

# Lovable diary prompts!
insults = [
"moron", "idiot", "fool"
]

# The ideal tsundere greeting is cold and hostile while betraying a
# lingering sense of affection. Constantly search for it.
prompts = [
# The BELOVED cold shoulder
#"... well, %s?",
#"... hello, %s?",
## Normal "'sup" prompts
#"... did you manage to accomplish anything today, %s?",
#"... so, %s, what did you manage to accomplish today, if anything?",
#"Hey %s - found any new ways to make a fool of yourself?",
#"How was your day, %s? Not that I care or anything...",
#"How have you been wasting your time lately, %s?",
#"What kind of stupid stuff were you up to today, %s?",
#"What kind of trouble did you get in today, %s?",
#"What did you do today, %s? As if that would impress me...",
#"It's your privilege that I'm wasting my time listening to you, %s...",
#"Don't get me wrong, %s, it's not like I'm worried about you.",
#"If you think I'm gonna miss you, think again, %s.",
#"I-it's not like I'm listening to you because I like you or anything, %s...", ## THIS RIGHT HERE
## More specific prompts
#"How did it go, %s? ... not that I'm expecting much!",
#"I'll forgive you, but just this time, got it, %s?",
#"... who do you think you are, %s?",
#"Why would you do that, %s? You are so foolish...",
## Calling the end-user an idiot
##"バカバカバカ！",
#"AAAAAH, %s, you idiot-idiot-idiot!",
#"%s, you're such a moron.",
#"%s, you're such an idiot.",
#"%s, you're such a fool.",
#"%s wa baka desu.",
#"%s no baka baka baka!",
#"Can you be any more clueless, %s?",
#"It's cute how you have no idea what's going on around you, %s.",
## Backhanded compliments
#"I guess you're smarter than you look, %s...",
#"You look so good today, %s! I didn't recognize you."
# make me happy
"Hi, %s!",
#"You look good today, %s!",
#"You may not know this, but you have many admirers, %s!",
#"You have a really nice smile, %s! Please smile more...",
"Tell me about your day, %s!",
"What made you happy today, %s? Even just a little thing...",
"What made you laugh today, %s?",
"What did you enjoy the most today, %s?",
"Feel free to let me know if something is bothering you, %s...",
#"I admire your optimism, %s!",
"I love listening to you, %s!",
#"I'm so lucky to have you, %s!",
#"I'm so happy I'm your friend, %s!",
#"I hope you can find happiness, %s!",
#"I really like your personality, %s!",
#"Keep on going, %s!",
"%s, m-may I have a hug?",
"%s, w-would you like a hug?",
u"%sのことが大好きです！(*/////∇/////*)",
]

# Set up Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.secret_key = '\xfbA6O\x1c\xa5\xfe\xb0(\x05\xa4 \xb8\x89)J2\xcb\xe4\xa7r"\x1b\x0e'
static_file_dir = os.path.dirname(os.path.realpath(__file__)) + '/static'

db = SQLAlchemy(app)

def uidify(string):
    return ''.join(c for c in string.lower().replace(' ', '-') if c.isalnum())

##############
# ORM objects

class User(db.Model):
    __tablename__ = 'user'
    sid = db.Column(db.String(24), primary_key=True, index=True, unique=True)
    name = db.Column(db.String(24), index=True, unique=True)
    passhash = db.Column(db.String(160))
    email = db.Column(db.String, unique=True)
    invite_key = db.Column(db.String(24))
    join_time = db.Column(db.DateTime, index=True)
    num_entries = db.Column(db.Integer, index=True)
    combo = db.Column(db.Integer, index=True)
    secret_days = db.Column(db.Integer)
    publicity = db.Column(db.Integer)

    def verify_password(self, password):
        salt = self.passhash[:32].encode('utf-8')
        return salt + hashlib.sha512(salt + password.encode('utf-8')).hexdigest().encode('utf-8') == self.passhash

    def __init__(self, name, password, email=None, invite_key=""):
        self.sid = uidify(name)
        self.name = name
        salt = uuid.uuid4().hex.encode('utf-8')
        self.passhash = salt + hashlib.sha512(salt + password.encode('utf-8')).hexdigest().encode('utf-8')
        self.invite_key = invite_key
        self.join_time = datetime.now()
        self.num_entries = 0
        self.combo = 0
        self.secret_days = 7
        # publicity  0: completely hidden  1: anyone with the link  2. link in user list
        self.publicity = 0

    def __repr__(self):
        return '<User %r>' % self.name

class Post(db.Model):
    __tablename__ = 'post'
    user_sid = db.Column(db.String(24), db.ForeignKey('user.sid'), primary_key=True, index=True)
    posted_date = db.Column(db.Date, primary_key=True, index=True)
    content = db.Column(db.String(8192))
    user = db.relationship('User',
        backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, user_sid, content, posted_date):
        self.user_sid = user_sid
        self.posted_date = posted_date
        self.content = content

    def __repr__(self):
        return '<Post by %r on %r>' % (self.user_sid, self.posted_date)

def init_db():
    db.drop_all()
    db.create_all()

def populate_db():
    admin = User("admin", "cake")
    bob = User("bob", "yolo")
    admin_1 = Post(admin.sid, "yolosshiku", date.today())
    admin_2 = Post(admin.sid, "good dame", date.today()-timedelta(days=1))
    admin_3 = Post(admin.sid, "hardy har", date.today()-timedelta(days=2))
    admin_4 = Post(admin.sid, "i cannot belief", date.today()-timedelta(days=7))
    admin_5 = Post(admin.sid, "i'm alive", date.today()-timedelta(days=365))
    bob_1 = Post(bob.sid, "what goodness", date.today())
    bob_2 = Post(bob.sid, "what cruelty", date.today()-timedelta(days=1))
    db.session.add(admin)
    db.session.add(admin_1)
    db.session.add(admin_2)
    db.session.add(admin_3)
    db.session.add(admin_4)
    db.session.add(admin_5)
    db.session.add(bob)
    db.session.add(bob_1)
    db.session.add(bob_2)
    db.session.commit()

############
# Utilities

def valid_date():
    # Particularly lenient; works as long as they are within 24h of UTC
    return (-1440 <= g.timezone <= 1440)

def their_time():
    # Gets the user's local time based on timezone cookie.
    utc_time = datetime.utcnow()
    their_time = utc_time - timedelta(minutes=g.timezone)
    return their_time

def their_date():
    return their_time().date()

def time_from_datestamp(ds):
    yyyy, mm, dd = map(int, [ds[0:4], ds[4:6], ds[6:8]])
    return date(yyyy, mm, dd)

def datestamp(d):
    return d.strftime("%Y%m%d")

@app.template_filter('prettydate')
def pretty_date(d):
    return d.strftime("%A, %B %-d, %Y")

@app.template_filter('markdown')
def my_markdown(t):
    return bleach.clean(markdown(t, extensions=['nl2br']),
            ['p', 'strong', 'em', 'br', 'img', 'ul', 'ol', 'li', 'a',
             'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
            {'img': ['src', 'alt', 'title'],
             'a': ['href']})

def datestamp_today():
    return datestamp(their_date())

def my_render_template(template_name, **kwargs):
    return render_template(template_name, login_name=g.username, login_user=g.user, **kwargs)

############
# App funcs

@app.before_request
def before_request():
    g.username = session.get('username')
    g.user = User.query.filter_by(name=g.username).first()
    g.timezone = int(request.cookies.get('timezone') or '0')

#############
# App routes

@app.errorhandler(404)
def page_not_found(e=None):
    return my_render_template('404.html'), 404

# Route static files
@app.route('/static/<path:filename>')
def static_file(filename):
    return send_from_directory(static_file_dir, filename)
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(static_file_dir, "favicon.ico")

# Dialog for importing a raw dump.
@app.route('/import_raw_dump')
def import_raw_dump():
    return my_render_template('import_raw_dump.html')

# Action performed for the above.
@app.route('/import_raw_dump', methods=['POST'])
def import_raw_dump_action():
    c = request.form.get('content')
    for line in (l.strip() for l in c.split('<br />')):
        if line:
            datestamp, content = line.split('\t')
            maidb.set_post(g.username, datestamp, Markup(content).unescape())
    return 'Done.'

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
    if valid_date():
        return_message = ""

        if 0 < len(content) <= 1000:
            new_post = Post(g.user.sid, content, their_date())
            db.session.merge(new_post)
            combo = 1
            return_message = "saved!"
        elif len(content) == 0:
            p = g.user.posts.filter_by(posted_date = their_date())
            if p:
                p.delete()
            combo = 0
            return_message = "deleted!"
        else:
            return_message = "onii-chan, it's too big! you're gonna split me in half!"

        db.session.commit()

        # Update number of entries
        g.user.num_entries = g.user.posts.count()
        # Update combo
        cd = their_date() - timedelta(days = 1)
        while g.user.posts.filter_by(posted_date = cd).first():
            combo += 1
            cd -= timedelta(days = 1)
        g.user.combo = combo

        db.session.commit()

        return return_message
    else:
        return "... you want to go on a date with me!?"

# Login attempts
@app.route('/attempt_login', methods=['POST'])
def attempt_login():
    u = request.form['username']
    p = request.form['password']
    user = User.query.filter_by(name = u).first()
    if user and user.verify_password(p):
        session['username'] = u
        return "Oh... welcome back, %s-sama." % u
    elif "'" in u or "'" in p:
        return "H-honto baka! Did you really think that would work?!"
    return "I don't recognize you, sorry."

# Logout
def logout():
    session.pop('username', None)
    return redirect('/')

# A certain selection of dates from a user's diary.
@app.route('/diary/<author_sid>/<dates>')
def diary(author_sid, dates):
    author = User.query.filter_by(sid = uidify(author_sid)).first()
    if author:
        if dates == 'all':
            posts = author.posts.order_by(Post.posted_date.desc()).all()
            template = 'dump.html'
        else:
            posts = author.posts.order_by(Post.posted_date.desc()).limit(author.secret_days+1).all()
            template = 'user.html'

        # Calculate date from which things should be hidden
        if g.user and author_sid == g.user.sid:
            hidden_day = their_date()
        elif author.publicity == 0:
            hidden_day = author.join_time.date() - timedelta(days = 1)
        else:
            hidden_day = their_date() - timedelta(days = author.secret_days)

        return my_render_template(
                template,
                author = author,
                num_entries = len(posts),
                posts = posts,
                hidden_day = hidden_day,
                #total_length = tl
                )
    else:
        return page_not_found()

# Last secret_days + 1 entries of a user's diary.
@app.route('/diary/<author_sid>')
def diary_preview(author_sid):
    return diary(author_sid, 'preview')

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
    if User.query.count() > 100 and invite_key != 'koi dorobou':
        return "Actually, we're out of spots for registrations. Sorry!"
    elif len(username) < 3:
        return 'Please enter a username at least 3 characters long.'
    elif len(password) < 3:
        return 'Please enter a password at least 3 characters long.'
    elif User.query.filter_by(sid=uidify(username)).first():
        return 'We already have someone with that name.'
    else:
        print('New user: %s/%s/%s' % (username, password, email))
        new_user = User(username, password)
        new_user.email = email
        new_user.invite_key = invite_key
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return 'welcome to the club!'

# List of users.
@app.route('/userlist')
def userlist():
    all_users = User.query.order_by(User.num_entries.desc()).filter(User.publicity >= 2).all()
    return my_render_template('userlist.html', all_users=all_users)

@app.route('/h-hello...')
def who_am_i():
    return my_render_template('what-is-this.html')

@app.route('/markdown')
def markdown_guide():
    return my_render_template('markdown-guide.html')

@app.route('/settings')
def edit_settings():
    if not g.user:
        return page_not_found()

    private = (g.user.publicity == 0)
    return my_render_template('settings.html', private=private)

@app.route('/change_setting', methods=['POST'])
def edit_settings_action():
    if not g.user:
        return page_not_found()

    setting_name = request.form.get('setting_name')
    setting_value = request.form.get('setting_value')

    if setting_name == 'private':
        g.user.publicity = 2 - int(setting_value) * 2
    elif setting_name == 'secret_days':
        print(setting_value)
        g.user.secret_days = int(setting_value)
        print(g.user.secret_days)
    else:
        return 'Nope.'
    db.session.commit()
    return 'Saved.'

# Index/home!
@app.route('/', methods=['GET', 'POST'])
def index():
    # handle logouts
    submit_action = request.form.get('action')
    if submit_action == 'logout':
        return logout()

    if g.user:
        today = their_date()

        current_post = g.user.posts.filter_by(posted_date = today).first()
        current_content = current_post.content if current_post else ""
        prompt = random.choice(prompts) % g.username

        old_posts = []
        deltas = [(1, "yesterday"), (7, "one week ago"), (30, "30 days ago"),
                  (90, "90 days ago"), (365, "365 days ago")]
        for delta, delta_name in deltas:
            day = today - timedelta(days=delta)
            print("checking", day)
            p = g.user.posts.filter_by(posted_date=day).first()
            if p:
                old_posts.append((delta_name, p))

        print(old_posts)

        return my_render_template(
                'write.html',
                old_posts = old_posts,
                prompt = prompt,
                current_content = current_content)
    else:
        return render_template('front.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG') or False)
