from tsundiary.views import *

# List of users.
@app.route('/userlist')
def userlist():
    all_users = (User.query.order_by(User.num_entries.desc())
            .filter(User.publicity >= 2)
            .filter(User.num_entries >= 2)
            .all())
    return render_template('userlist.html', all_users=all_users)

# List of users (sorted by latest new post)
@app.route('/userlist/latest')
def userlist_latest():
    all_users = (User.query.order_by(User.latest_post_date.desc())
            .order_by(User.num_entries.desc())
            .filter(User.publicity >= 2)
            .filter(User.num_entries >= 2)
            .filter(User.latest_post_date >= date.today() - timedelta(days=1))
            .all())
    return render_template('userlist.html', all_users=all_users)

# List of users (including throwaways).
@app.route('/userlist/all')
def userlist_all():
    all_users = (User.query.order_by(User.latest_post_date.desc())
            .order_by(User.num_entries.desc())
            .filter(User.publicity >= 2)
            .filter(User.num_entries >= 1)
            .all())
    return render_template('userlist.html', all_users=all_users)
