from flask import g, render_template, request

from tsundiary import app
from tsundiary.views import page_not_found
from tsundiary.models import db

@app.route('/settings')
def edit_settings():
    if not g.user:
        return page_not_found()

    private = (g.user.publicity == 0)
    return render_template('settings.html', private=private)

@app.route('/change_setting', methods=['POST'])
def edit_settings_action():
    if not g.user:
        return page_not_found()

    setting_name = request.form.get('setting_name')
    setting_value = request.form.get('setting_value')

    if setting_name == 'private':
        # True
        if int(setting_value):
            g.user.publicity = 0
        else:
            g.user.publicity = 2
        db.session.commit()
        return 'saved!'
    elif setting_name == 'secret_days':
        if setting_value == 'Hidden':
            g.user.publicity = 1
        elif setting_value == 'Forever':
            g.user.publicity = 0
        else:
            g.user.publicity = 2
            g.user.secret_days = int(setting_value)
        db.session.commit()
        return 'saved!'
    elif setting_name == 'theme':
        g.user.theme = setting_value
        db.session.commit()
        return 'refresh to see theme'
    elif setting_name == 'color':
        # User selection of color is taken as a suggestion only.
        # Each theme will incorporate the colors differently.
        g.user.color = setting_value
        print("I am now a", g.user.color)
        db.session.commit()
        return 'refresh to see color'
    else:
        return 'error'
    return 'Jim messed up'

@app.route('/change_password', methods=['POST'])
def change_password():
    if not g.user:
        return page_not_found()

    old_pass = request.form.get('old_pass')
    new_pass = request.form.get('new_pass')

    if len(new_pass) < 3:
        return 'Please enter a new password at least 3 characters long.'

    if g.user.verify_password(old_pass):
        g.user.set_password(new_pass)
        db.session.commit()
        return 'password changed!'
    else:
        return 'wrong old password'
