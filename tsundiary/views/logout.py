from flask import g, request, session, redirect

from tsundiary import app

# Logout
@app.route('/logout')
def logout():
    if g.user and request.args.get('user') == g.user.sid:
        session.pop('user_sid', None)
    return redirect('/')
