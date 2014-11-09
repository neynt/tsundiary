# This was used for a database migration before I discovered the magic of Alembic.
import tsundiary
from datetime import datetime, date
tsundiary.init_db()
postfile = open('/home/neynt/TSUN-POSTS').read().strip().split('[NEWENTRY]')
userfile = open('/home/neynt/TSUN-USERS').read().strip().split('[NEWENTRY]')

post_dates = {}

for l in userfile:
    name, password, email, invite_key = l.split('[COLSEP]')
    print("migrating user %s" % name)
    new_user = tsundiary.User(name, password, email, invite_key)
    new_user.publicity = 1
    tsundiary.db.session.add(new_user)
print("committing")
tsundiary.db.session.commit()

for p in postfile:
    username, datestamp, content = p.split('[COLSEP]')
    user_sid = tsundiary.uidify(username)
    if tsundiary.User.query.filter_by(sid=user_sid).count() <= 0:
        print("Skipping %s" % user_sid)
        continue
    print("migrating post by %s on %r" % (user_sid, datestamp))
    new_post = tsundiary.Post(user_sid, content, tsundiary.time_from_datestamp(datestamp))
    if user_sid in post_dates:
        post_dates[user_sid].append(tsundiary.time_from_datestamp(datestamp))
    else:
        post_dates[user_sid] = []
        post_dates[user_sid].append(tsundiary.time_from_datestamp(datestamp))
    tsundiary.db.session.add(new_post)
print("committing")
tsundiary.db.session.commit()

for u in tsundiary.User.query.all():
    if u.sid in post_dates:
        mindate = min(post_dates[u.sid])
        print("setting join date of %s to %r" % (u.sid, mindate))
        u.join_time = datetime.combine(mindate, datetime.min.time())
print("committing")
tsundiary.db.session.commit()
