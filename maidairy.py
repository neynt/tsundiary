import os
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, send_from_directory, redirect, session, request

########################
# Initialization vectors

# Set up database
conn_string = "host='ec2-107-22-182-174.compute-1.amazonaws.com' dbname='d7lda6chqa8526' user='gnfcfjnsbihezp' password='7jvgKFTp6p09KuiQdf0-rDHnT8'"
conn = psycopg2.connect(conn_string)
#cur = conn.cursor('the_only_cursor', cursor_factory=psycopg2.extras.DictCursor)
cur = conn.cursor()

# Set up Flask app
app = Flask(__name__)
app.secret_key = '\xfbA6O\x1c\xa5\xfe\xb0(\x05\xa4 \xb8\x89)J2\xcb\xe4\xa7r"\x1b\x0e'
static_file_dir = os.path.dirname(os.path.realpath(__file__)) + '/static'

####################
# Database functions

def init_db():
    cur.execute('DROP TABLE IF EXISTS posts')
    cur.execute('CREATE TABLE posts ( postid varchar(80), content varchar(500) )')
    cur.execute('DROP TABLE IF EXISTS users')
    cur.execute('CREATE TABLE users ( username varchar(24), password varchar(24), favour integer )')
    cur.execute('INSERT INTO users VALUES ( %s, %s, %s )', ["Neynt", "ke-ki", 69])
    conn.commit()
    return

def get_gold(username):
    cur.execute("SELECT favour FROM users WHERE username=%s", [username])
    result = cur.fetchone()
    if result:
        return result[0]

def set_gold(username):
    cur.execute("UPDATE users SET favour = favour + 1 WHERE username=%s", [username])
    conn.commit()
    return

def valid_login(username, password):
    cur.execute("SELECT username FROM users WHERE username=%s AND password=%s", [username, password])
    # Will return a null value if user does not exist
    return cur.fetchone()

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
        return "Thanks."
    else:
        return "Invalid date, baka."

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
        return render_template('logged_in_front.html', username=session['username'])
    else:
        return render_template('front.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
