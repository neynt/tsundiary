import os
from flask import Flask

app = Flask(__name__)
desu = 0

@app.route('/')
def index():
    global desu
    desu += 1
    return 'maidairy ni youkoso! numero %d desu' % desu

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
