# encoding=utf-8
import os
import random
import datetime
from flask import Flask, render_template, send_from_directory, redirect, session, request, g
import maidb

########################
# Initialization vectors

# Lovable diary prompts!
insults = [
"moron", "idiot"
]
prompts = [
# Normal "'sup" prompts
"... what did you manage to accomplish today?",
"Tell me what happened today. Not that I care or anything...",
"What kind of stupid stuff were you up to today, idiot?",
"What trouble did you get in today, moron?",
"What did you do today? As if that would impress me...",
"... well?",
# Topic-specific prompts
"How did it go? You got rejected, right?",
"So when are you finally going to realize?",
"Don't get me wrong, it's not like I'm worried about you.",
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
    # Return a datetime object with the user's local time.
    utc_time = datetime.datetime.utcnow()
    their_time = utc_time - datetime.timedelta(minutes=g.timezone)
    return their_time

def datestamp(d):
    return d.strftime("%Y%m%d")

def datestamp_today():
    return datestamp(their_time())

# Selected old entries from special time intervals.
def selected_old_entries():
    t = their_time()

    # Yesterday
    d = t - datetime.timedelta(days=1)
    p = maidb.get_post(g.username, datestamp(d))
    if p:
        yield ('Yesterday', p)

    # Same day last week
    d = t - datetime.timedelta(days=7)
    p = maidb.get_post(g.username, datestamp(d))
    if p:
        yield ('%s (one week ago)' % d.strftime("%A, %B %d"), p)

    # Same day# of last month
    try:
        if t.month == 1:
            d = t.replace(year=t.year-1, month=12)
        else:
            d = t.replace(month=t.month-1)

        p = maidb.get_post(g.username, datestamp(d))
        if p:
            yield ('%s (one month ago)' % d.strftime("%A, %B %d, %Y"), p)

        if (t + datetime.timedelta(days=1)).month != t.month:
            # This is the last day of the month, do all the days that would be missed.
            orig_m = d.month
            d += datetime.timedelta(days=1)
            while d.month == orig_m:
                yield ('%s' % d.strftime("%A, %B %d, %Y"))
    except ValueError:
        # This month has more days than the last month.
        pass

    # 90 days ago
    d = t - datetime.timedelta(days=90)
    p = maidb.get_post(g.username, datestamp(d))
    if p:
        yield ('%s (90 days ago)' % d.strftime("%A, %B %d"), p)

    # Same day last year
    try:
        d = t.replace(year=t.year-1)
        p = maidb.get_post(g.username, datestamp(d))
        if p:
            yield ('%s (this day last year)' % d.strftime("%A, %B %d, %Y"), p)
    except ValueError:
        # It's March 29, probably.
        pass

############
# App funcs

@app.before_request
def before_request():
    g.username = session.get('username')
    g.timezone = int(request.cookies.get('timezone'))

#############
# App routes

# Route static files
@app.route('/static/<path:filename>')
def static_file(filename):
    return send_from_directory(static_file_dir, filename)

# Import a raw dump.
@app.route('/import_raw_dump')
def import_raw_dump():
    return render_template('import_raw_dump.html')

# Action performed for the above.
@app.route('/import_raw_dump', methods=['POST'])
def import_raw_dump_action():
    c = request.form.get('content').splitlines()
    for date, content in zip(c[0::2], c[1::2]):
        y, m, d = map(int, date.split('-'))
        ds = datestamp(datetime.date(year=y, month=m, day=d))
        #print ds, content
        maidb.set_post(session['username'], ds, content)
    return 'Done.'

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
        if 1 <= len(c) <= 500:
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
        return "H-hontō baka! Did you really think that would work?!"
    return "Idiot. Can't you at least get your login right?"

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

# Dump a user's entire diary.
@app.route('/diary/<author>')
def diary(author):
    entries = sorted(maidb.get_all_posts(author), reverse=True)
    return render_template('dump.html',
            login_name = g.username,
            username = author,
            entries = entries)

# Index/home!
@app.route('/')
def index():
    if g.username:
        current_content = maidb.get_post(g.username, datestamp_today())
        return render_template('front_logged_in.html',
                login_name = g.username,
                old_entries = selected_old_entries(),
                prompt = random.choice(prompts),
                current_content = current_content)
    else:
        return render_template('front.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
