from flask import request, session, flash, redirect

from tsundiary import app
from tsundiary.utils import uidify
from tsundiary.models import User

# Login attempts
@app.route('/attempt_login', methods=['POST'])
def attempt_login():
    u = request.form['username']
    p = request.form['password']
    user = User.query.filter_by(sid = uidify(u)).first()
    if user and user.verify_password(p):
        session['user_sid'] = uidify(u)
        session.permanent = True
        return redirect('/')
    elif "'" in u or "'" in p:
        flash('H-honto baka!')
    else:
        flash("I don't recognize you, sorry.")
    return redirect('/')
