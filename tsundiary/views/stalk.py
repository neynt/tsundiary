from tsundiary.views import *

# Stalk users.
@app.route('/stalk')
def stalk_list():
    return render_template('stalk.html')
