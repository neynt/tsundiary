from tsundiary.views import *

# User registration form.
@app.route('/register')
def register():
    return render_template('register.html')

# registration action
@app.route('/register', methods=['POST'])
def register_action():
    invite_key = request.form.get('invite_key')
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email') or None

    # check if we already have too many users
    if User.query.count() > 400 and invite_key != 'koi dorobou':
        flash("Actually, we're out of spots for registrations. Sorry!")
    elif len(username) < 2:
        flash("Please enter a username at least 2 characters long.")
    elif len(password) < 3:
        flash("Please enter a password at least 3 characters long.")
    elif User.query.filter_by(sid=uidify(username)).first():
        flash("We already have someone with that name.")
    else:
        new_user = User(username, password)
        new_user.email = email
        new_user.invite_key = invite_key
        db.session.add(new_user)
        db.session.commit()
        session['user_sid'] = new_user.sid
        session.permanent = True
        return redirect('/')
    return redirect('/register')

