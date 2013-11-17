# coding=utf-8
from datetime import datetime, date
import maiconfig
import psycopg2
import psycopg2.extras
#import bcrypt

# Set up database
#conn_string = "host='ec2-107-22-182-174.compute-1.amazonaws.com' dbname='d7lda6chqa8526' user='gnfcfjnsbihezp' password='7jvgKFTp6p09KuiQdf0-rDHnT8'"
conn_string = "host='localhost' dbname='tsundiary' user='neynt' password='m_w2TwoK'"
conn = psycopg2.connect(conn_string)
#cur = conn.cursor('the_only_cursor', cursor_factory=psycopg2.extras.DictCursor)
cur = conn.cursor()

# Helper functions
def uidify(string):
    return ''.join(c for c in string.lower().replace(' ', '-') if c.isalnum())

# Database functions
def valid_login(username, password):
    cur.execute("SELECT passhash FROM users WHERE username=%s", [username])
    result = cur.fetchone()
    if result:
        passhash = result[0]
        return bcrypt.hashpw(password.encode('utf-8'), passhash) == passhash
    else:
        return False

def user_exists(username):
    cur.execute("SELECT username FROM users WHERE LOWER(username)=LOWER(%s)", [username])
    return cur.fetchone() or False

def create_new_user(username, password, email, invite_key):
    userid = uidify(username)
    passhash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10))
    cur.execute("""INSERT INTO users
        (userid, username, passhash, email, invite_key,
        create_date, combo, secret_days) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        [userid, username, passhash, email, invite_key,
        date.today(), 0, 7])
    conn.commit()

def get_all_usernames():
    cur.execute("SELECT username FROM users")
    for r in cur:
        yield r[0]

def get_top_users(start=0, count=10):
    cur.execute("SELECT username FROM users ORDER BY combo LIMIT %s OFFSET %s", [count, start])

def set_post(username, datestamp, content):
    #content_enc = content.encode('utf-8')
    if len(content) > 0:
        if get_post(username, datestamp) != []:
            cur.execute("UPDATE posts SET content=%s WHERE username=%s AND datestamp=%s",
                    [content, username, datestamp])
        else:
            cur.execute("INSERT INTO posts (username, datestamp, content) VALUES (%s, %s, %s)",
                    [username, datestamp, content])
    else:
        cur.execute("DELETE FROM posts WHERE username=%s AND datestamp=%s", [username, datestamp])
    conn.commit()


def get_post(username, datestamp):
    cur.execute("SELECT content FROM posts WHERE username=%s AND datestamp=%s", [username, datestamp])
    result = cur.fetchone()
    if result:
        return result[0].decode('utf-8')
    else:
        return []

def get_all_posts(username):
    cur.execute("SELECT datestamp, content FROM posts WHERE username=%s ORDER BY datestamp DESC", [username])
    for r in cur:
        yield (r[0], r[1].decode('utf-8'))

def init_db():
    cur.execute('DROP TABLE IF EXISTS users')
    cur.execute('''CREATE TABLE users (
        userid varchar(24) primary key,
        username varchar(24) index,
        passhash char(60),
        email varchar(48),
        invitekey varchar(24),
        create_date date index,
        combo integer,
        secret_days integer
    )''')
    cur.execute('DROP TABLE IF EXISTS posts')
    cur.execute('''CREATE TABLE posts (
        userid varchar(24) primary key,
        datestamp date primary key,
        content varchar(5000)
    )''')
    conn.commit()
    return

def populate():
    # Populate the db with test data.
    create_new_user("Neynt", "ke-ki", "hyriodula@gmail.com", "koi dorobou")
