from tsundiary.views import *

# User registration form.
@app.route('/register')
def register():
    cur_username = session.get('cur_username') or ''
    cur_email = session.get('cur_email') or ''
    cur_password = session.get('cur_password') or ''
    return render_template('register.html', cur_username = cur_username, cur_email = cur_email, cur_password = cur_password)

# registration action
@app.route('/register', methods=['POST'])
def register_action():
    invite_key = request.form.get('invite_key')
    username = request.form.get('username')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    email = request.form.get('email') or None

    # temporary session variables for registration
    session['cur_username'] = username
    session['cur_email'] = email
    session['cur_password'] = password

    # propriety checks
    if User.query.count() > 400 and invite_key != 'koi dorobou':
        flash("Actually, we're out of spots for registrations. Sorry!")
    elif password != password_confirm:
        flash("Please make sure that your passwords match.")
    elif len(username) < 2:
        flash("Please enter a username at least 2 characters long.")
    elif len(password) < 3:
        flash("Please enter a password at least 3 characters long.")
    elif User.query.filter_by(sid=uidify(username)).first():
        flash("We already have someone with that name.")
        session['cur_username'] = ''
    else:
        new_user = User(username, password)
        new_user.email = email
        new_user.invite_key = invite_key
        db.session.add(new_user)
        db.session.commit()
        session['user_sid'] = new_user.sid
        session.permanent = True

        # clear old session vars
        session['cur_username'] = ''
        session['cur_email'] = ''
        session['cur_password'] = ''

        return redirect('/')

    # failed, send 'em back to the form
    return redirect('/register')
