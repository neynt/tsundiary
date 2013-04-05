import os
import psycopg2
import psycopg2.extras
from flask import Flask, render_template

# Set up Flask app
app = Flask(__name__)
desu = 0

# Set up database
conn_string = "host='ec2-107-22-182-174.compute-1.amazonaws.com' dbname='d7lda6chqa8526' user='gnfcfjnsbihezp' password='7jvgKFTp6p09KuiQdf0-rDHnT8'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)

@app.route('/')
def index():
    global desu
    desu += 1
    return render_template('front.html', num=desu)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
