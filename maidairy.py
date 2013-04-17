import os
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, send_from_directory, redirect, session, request

########################
# Initialization vectors

# Config
USE_POSTGRES = True

if USE_POSTGRES:
    # Set up database
    conn_string = "host='ec2-107-22-182-174.compute-1.amazonaws.com' dbname='d7lda6chqa8526' user='gnfcfjnsbihezp' password='7jvgKFTp6p09KuiQdf0-rDHnT8'"
    conn = psycopg2.connect(conn_string)
    #cur = conn.cursor('the_only_cursor', cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
else:
    db = {t: {} for t in ['users', 'posts']}
    db['users']['Neynt'] = {'password': 'ke-ki', 'favour':690}

# Set up Flask app
app = Flask(__name__)
app.secret_key = '\xfbA6O\x1c\xa5\xfe\xb0(\x05\xa4 \xb8\x89)J2\xcb\xe4\xa7r"\x1b\x0e'
static_file_dir = os.path.dirname(os.path.realpath(__file__)) + '/static'

############
# Utilities

def valid_date(d):
    return True

def datestamp_today():
    return 'Tue Apr 16 2013'

def post_id(username, date):
    return "%s %s" % (username, date)

####################
# Database functions

def init_db():
    cur.execute('DROP TABLE IF EXISTS users')
    cur.execute('CREATE TABLE users ( username varchar(24), password varchar(24), favour integer )')
    cur.execute('INSERT INTO users VALUES ( %s, %s, %s )', ["Neynt", "ke-ki", 69])
    cur.execute('DROP TABLE IF EXISTS posts')
    cur.execute('CREATE TABLE posts ( username varchar(24), datestamp varchar(24), content varchar(500) )')
    conn.commit()
    return

if USE_POSTGRES:
    def get_gold(username):
        cur.execute("SELECT favour FROM users WHERE username=%s", [username])
        result = cur.fetchone()
        if result:
            return result[0]

    def set_gold(username):
        cur.execute("UPDATE users SET favour = favour + 1 WHERE username=%s", [username])
        conn.commit()

    def valid_login(username, password):
        cur.execute("SELECT username FROM users WHERE username=%s AND password=%s", [username, password])
        if cur.fetchone():
            return True
        else:
            return False

    def get_post(username, datestamp):
        cur.execute("SELECT content FROM posts WHERE username=%s AND datestamp=%s", [username, datestamp])
        result = cur.fetchone()
        if result:
            return result[0]
        else:
            return ''

    def set_post(username, datestamp, content):
        if get_post(username, datestamp):
            cur.execute("UPDATE posts SET content=%s WHERE username=%s AND datestamp=%s",
                    [content, username, datestamp])
        else:
            cur.execute("INSERT INTO posts (username, datestamp, content) VALUES (%s, %s, %s)",
                    [username, datestamp, content])
        conn.commit()
else:
    def get_gold(username):
        return db['users'][username]['favour']

    def set_gold(username):
        db['users'][username]['favour'] += 1

    def valid_login(username, password):
        try:
            return db['users'][username]['password'] == password
        except KeyError:
            return False

    def get_post(username, datestamp):
        try:
            return db['posts'][(username, datestamp)]
        except KeyError:
            return None

    def set_post(username, datestamp, content):
        db['posts'][(username, datestamp)] = content

#############
# App routes

# Route static files
@app.route('/static/<path:filename>')
def static_file(filename):
    return send_from_directory(static_file_dir, filename)

# Updating content
@app.route('/confess', methods=['POST'])
def confess():
    d = request.form['date']
    c = request.form['content']
    if valid_date(d):
        if len(c) <= 500:
            set_post(session['username'], d, c)
            print(d, c)
            return "saved!"
        else:
            return "too long, baka."
    else:
        return "bad date, baka."

# Login attempts
@app.route('/attempt_login', methods=['POST'])
def attempt_login():
    u = request.form['username']
    p = request.form['password']
    if valid_login(u, p):
        session['username'] = u
        return "Welcome, %s-sama." % u
    return "Dude, you have no soul."

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

# Index/home!
@app.route('/')
def index():
    if 'username' in session:
        current_content = get_post(session['username'], datestamp_today())
        return render_template('front_logged_in.html',
                username=session['username'],
                current_content=current_content)
    else:
        return render_template('front.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
