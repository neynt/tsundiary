from tsundiary.views import *

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
        #return "Oh... welcome back, %s-sama." % u
    elif "'" in u or "'" in p:
        flash('H-honto baka!')
        #return "H-honto baka! Did you really think that would work?!"
    flash("I don't recognize you, sorry.")
    return redirect('/')
    #return "I don't recognize you, sorry."

