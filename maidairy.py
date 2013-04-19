import os
import datetime
from flask import Flask, render_template, send_from_directory, redirect, session, request, g
import maidb

########################
# Initialization vectors

# Set up Flask app
app = Flask(__name__)
app.secret_key = '\xfbA6O\x1c\xa5\xfe\xb0(\x05\xa4 \xb8\x89)J2\xcb\xe4\xa7r"\x1b\x0e'
static_file_dir = os.path.dirname(os.path.realpath(__file__)) + '/static'

############
# Utilities

def valid_date(d):
    return True

def datestamp_today():
    utc_time = datetime.datetime.utcnow()
    their_time = utc_time - datetime.timedelta(hours=int(g.timezone)/60)
    result = their_time.strftime("%a %b %d %Y")
    print("Our time is", utc_time, ". After taking into account", g.timezone, ", their time is %s." % (result))
    return result

############
# App funcs

@app.before_request
def before_request():
    g.username = session.get('username')
    g.timezone = request.cookies.get('timezone')

#############
# App routes

# Route static files
@app.route('/static/<path:filename>')
def static_file(filename):
    return send_from_directory(static_file_dir, filename)

# Updating content (aka AI NO KOKUHAKU SURU)
@app.route('/confess', methods=['POST'])
def confess():
    d = request.form.get('date')
    c = request.form.get('content').strip()
    print("Received %s for %s." % (c, d))
    if valid_date(d):
        if 1 <= len(c) <= 500:
            maidb.set_post(session['username'], d, c)
            print(d, c)
            return "saved!"
        else:
            return "bad length, baka."
    else:
        return "... you want to go on a date with me, baka!?"

# Login attempts
@app.route('/attempt_login', methods=['POST'])
def attempt_login():
    u = request.form['username']
    p = request.form['password']
    if maidb.valid_login(u, p):
        session['username'] = u
        return "Oh... welcome back, %s-sama." % u
    return "Idiot. Can't you at least get your login right?"

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

# Dump a user's entire diary.
@app.route('/diary/<author>')
def diary(author):
    entries = list(maidb.get_all_posts(author))
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
                current_content = current_content)
    else:
        return render_template('front.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
