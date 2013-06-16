# coding=utf-8
import maiconfig
import psycopg2
import psycopg2.extras

# Set up database
if maiconfig.USE_POSTGRES:
    conn_string = "host='ec2-107-22-182-174.compute-1.amazonaws.com' dbname='d7lda6chqa8526' user='gnfcfjnsbihezp' password='7jvgKFTp6p09KuiQdf0-rDHnT8'"
    conn = psycopg2.connect(conn_string)
    #cur = conn.cursor('the_only_cursor', cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
else:
    db = {t: {} for t in ['users', 'posts']}
    db['users']['Neynt'] = {'password': 'ke-ki', 'favour':690}
    db['users']['guest'] = {'password': 'guest', 'favour':690}
    db['posts'][('Neynt', '20130419')] = u'The day it all started.'
    db['posts'][('Neynt', '20130418')] = u'The dawn of the storm. がんばってね！'

# Database functions
def init_db():
    cur.execute('DROP TABLE IF EXISTS users')
    cur.execute('CREATE TABLE users ( username varchar(24), password varchar(24), email varchar(48), invitekey varchar(24) )')
    cur.execute('INSERT INTO users VALUES ( %s, %s, %s )', ["Neynt", "ke-ki", 69])
    cur.execute('DROP TABLE IF EXISTS posts')
    cur.execute('CREATE TABLE posts ( username varchar(24), datestamp varchar(24), content varchar(5000) )')
    conn.commit()
    return

# There are two variations: one using python dicts (for testing), one using postgres.
if maiconfig.USE_POSTGRES:
    def valid_login(username, password):
        cur.execute("SELECT username FROM users WHERE username=%s AND password=%s", [username, password])
        return cur.fetchone() or False

    def user_exists(username):
        cur.execute("""SELECT username FROM users WHERE LOWER(username)=LOWER(%s)""", [username])
        return cur.fetchone() or False

    def create_new_user(username, password, email, invite_key):
        cur.execute("""INSERT INTO users (username, password, email, invitekey) VALUES (%s, %s, %s, %s)""", [username, password, email, invite_key])
        return

    def get_all_usernames():
        cur.execute("""SELECT username FROM users""")
        for r in cur:
            yield r[0]

    def get_post(username, datestamp):
        cur.execute("SELECT content FROM posts WHERE username=%s AND datestamp=%s", [username, datestamp])
        result = cur.fetchone()
        if result:
            return result[0].decode('utf-8')
        else:
            return []

    def set_post(username, datestamp, content):
        #content_enc = content.encode('utf-8')
        if get_post(username, datestamp) != []:
            cur.execute("UPDATE posts SET content=%s WHERE username=%s AND datestamp=%s",
                    [content, username, datestamp])
        else:
            cur.execute("INSERT INTO posts (username, datestamp, content) VALUES (%s, %s, %s)",
                    [username, datestamp, content])
        conn.commit()

    def get_all_posts(username):
        cur.execute("SELECT datestamp, content FROM posts WHERE username=%s ORDER BY datestamp", [username])
        for r in cur:
            yield (r[0].decode('utf-8'), r[1].decode('utf-8'))

else:
    def valid_login(username, password):
        try:
            return db['users'][username]['password'] == password
        except KeyError:
            return ''

    def get_post(username, datestamp):
        try:
            return db['posts'][(username, datestamp)]
        except KeyError:
            return None

    def set_post(username, datestamp, content):
        db['posts'][(username, datestamp)] = content

    def get_all_posts(username):
        for key, content in db['posts'].items():
            username, datestamp = key
            yield (datestamp, content)
