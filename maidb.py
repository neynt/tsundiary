import psycopg2
import psycopg2.extras

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
            return result[0].decode('utf-8')
        else:
            return []

    def set_post(username, datestamp, content):
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
    def get_gold(username):
        return db['users'][username]['favour']

    def set_gold(username):
        db['users'][username]['favour'] += 1

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

