# encoding=utf-8
import os
import random
import datetime
from flask import Flask, Markup, render_template, send_from_directory, redirect, session, request, g
import maiconfig
import maidb

########################
# Initialization vectors

# Lovable diary prompts!
insults = [
"moron", "idiot", "fool"
]
prompts = [
# The BELOVED cold shoulder
"...",
"... well?",
# Normal "'sup" prompts
"... did you manage to accomplish anything today?",
"Hey - found any new ways to make a fool of yourself?",
"How was your day? Not that I care or anything...",
"How have you been wasting your time lately?",
"What kind of stupid stuff were you up to today, idiot?",
"What kind of trouble did you get in today, moron?",
"What did you do today? As if that would impress me...",
"It's your privilege that I'm wasting my time listening to you...",
# More specific prompts
"How did it go? ... not that I'm expecting much!",
"Don't get me wrong, it's not like I'm worried about you.",
"If you think I'm gonna miss you, think again.",
"I'll forgive you, but just this time, got it?",
"I-it's not like I'm listening to you because I like you or anything...",
# Calling the end-user an idiot
#"バカバカバカ！",
"AAAAAH, you idiot-idiot-idiot!",
"Ba~ka.",
"Baka baka baka!",
"Can you be any more clueless?",
]

# Set up Flask app
app = Flask(__name__)
app.secret_key = '\xfbA6O\x1c\xa5\xfe\xb0(\x05\xa4 \xb8\x89)J2\xcb\xe4\xa7r"\x1b\x0e'
static_file_dir = os.path.dirname(os.path.realpath(__file__)) + '/static'

############
# Utilities

def valid_date():
    # Particularly lenient; works as long as they are within 24h of UTC
    return (-1440 <= g.timezone <= 1440)

def their_time():
    # Gets the user's local time based on timezone cookie.
    utc_time = datetime.datetime.utcnow()
    their_time = utc_time - datetime.timedelta(minutes=g.timezone)
    return their_time

def time_from_datestamp(d):
    yyyy, mm, dd = map(int, [d[0:4], d[4:6], d[6:8]])
    return datetime.date(yyyy, mm, dd)

def datestamp(d):
    return d.strftime("%Y%m%d")

def datestamp_today():
    return datestamp(their_time())

# Selected old entries from special time intervals.
def selected_old_entries():
    today = their_time()

    # Yesterday
    d = today - datetime.timedelta(days=1)
    p = maidb.get_post(g.username, datestamp(d))
    if p:
        yield ('Yesterday', p)

    # Same day last week
    d = today - datetime.timedelta(days=7)
    p = maidb.get_post(g.username, datestamp(d))
    if p:
        yield ('%s (one week ago)' % d.strftime("%A, %B %d"), p)

    # 30 days ago
    d = today - datetime.timedelta(days=30)
    p = maidb.get_post(g.username, datestamp(d))
    if p:
        yield ('%s (30 days ago)' % d.strftime("%A, %B %d"), p)

    # 90 days ago
    d = today - datetime.timedelta(days=90)
    p = maidb.get_post(g.username, datestamp(d))
    if p:
        yield ('%s (90 days ago)' % d.strftime("%A, %B %d"), p)

    # 365 days ago
    d = today - datetime.timedelta(days=365)
    p = maidb.get_post(g.username, datestamp(d))
    if p:
        yield ('%s (365 days ago)' % d.strftime("%A, %B %d"), p)

# Make a post HTML-pretty.
# Currently does nothing, but may do markdown in the future.
def prettify(text):
    return text

# Process a list of entry tuples.
def format_entries(entries):
    new_list = []
    for title, content in entries:
        new_list.append((title, prettify(content)))
    return new_list

def my_render_template(template_name, **kwargs):
    return render_template(template_name, login_name=g.username, **kwargs)

############
# App funcs

@app.before_request
def before_request():
    g.username = session.get('username')
    g.timezone = int(request.cookies.get('timezone') or '0')

#############
# App routes

# Route static files
@app.route('/static/<path:filename>')
def static_file(filename):
    return send_from_directory(static_file_dir, filename)

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

    # Old deprecated format.
    #for date, content in zip(c[0::2], c[1::2]):
    #    y, m, d = map(int, date.split('-'))
    #    ds = datestamp(datetime.date(year=y, month=m, day=d))
    #    #print ds, content
    #    maidb.set_post(session['username'], ds, content)
    #return 'Done.'

# Raw dump for data liberation.
@app.route('/raw_dump')
def raw_dump():
    if not g.username:
        return "Login kudasai."
    entries = maidb.get_all_posts(g.username)
    return render_template('raw_dump.html',
                           entries=entries)

# Updating content (aka AI NO KOKUHAKU SURU)
@app.route('/confess', methods=['POST'])
def confess():
    c = request.form.get('content').strip()
    if valid_date():
        if 1 <= len(c) <= 1000:
            maidb.set_post(session['username'], datestamp_today(), c)
            return "saved!"
        else:
            return "..."
    else:
        return "... you want to go on a date with me!?"

# Login attempts
@app.route('/attempt_login', methods=['POST'])
def attempt_login():
    u = request.form['username']
    p = request.form['password']
    if maidb.valid_login(u, p):
        session['username'] = u
        return "Oh... welcome back, %s-sama." % u
    elif "'" in u or "'" in p:
        return "H-hontou baka! Did you really think that would work?!"
    return "Idiot. Can't you at least get your login right?"

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

# Dump a user's entire diary.
@app.route('/diary/<author>')
def diary(author):
    entries = format_entries(sorted(maidb.get_all_posts(author), reverse=True))
    written_dates  = set(e[0] for e in entries)
    day = their_time()

    # Don't break combo for missing current day
    if datestamp(day) in written_dates:
        consec = 1
    else:
        consec = 0

    day -= datetime.timedelta(days=1)

    while datestamp(day) in written_dates:
        day -= datetime.timedelta(days=1)
        consec += 1

    return my_render_template(
            'dump.html',
            username = author,
            date_of_start = time_from_datestamp(min(x[0] for x in entries)).strftime("%x") if entries else "an unknown day",
            num_entries = len(entries),
            combo = consec,
            entries = entries
            )

# User registration form.
@app.route('/register')
def register():
    return my_render_template('register.html')

# registration action
@app.route('/register', methods=['POST'])
def register_action():
    invite_key = request.form.get('invite_key')
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email') or ''
    if invite_key != 'koi dorobou':
        return 'bad invite key.'
    elif maidb.user_exists(username):
        return 'that person already exists.'
    else:
        print('%s %s %s' % (username, password, email))
        maidb.create_new_user(username, password, email, invite_key)
        session['username'] = username
        return 'Welcome to the club.'

# List of users.
@app.route('/userlist')
def userlist():
    all_users = list(maidb.get_all_usernames())
    return my_render_template('userlist.html', all_users=all_users)

# Index/home!
@app.route('/')
def index():
    if g.username:
        current_content = maidb.get_post(g.username, datestamp_today())
        return my_render_template(
                'front_logged_in.html',
                old_entries = format_entries(selected_old_entries()),
                prompt = random.choice(prompts),
                current_content = current_content)
    else:
        return render_template('front.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=maiconfig.TESTING)
