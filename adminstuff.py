from tsundiary import User, Post, db
from datetime import date, datetime, timedelta

def delete_user(sid):
    Post.query.filter_by(user_sid=sid).delete()
    User.query.filter_by(sid=sid).delete()
    db.session.commit()

def user_from_sid(sid):
    return User.query.filter_by(sid=sid).first()

def graph_all_posts():
    posts = Post.query.all()
    d = min(p.posted_date for p in posts)
    while d < date.today():
        print("%s, %d" % (d, len([p for p in posts if p.posted_date == d])))
        d += timedelta(days=1)

def get_active_users():
    users = {}
    for p in Post.query.filter(Post.posted_date >= date.today() - timedelta(days=6)).all():
        if p.user_sid not in users:
            users[p.user_sid] = 0
        users[p.user_sid] += 1

    upairs = users.items()
    upairs.sort()
    upairs.sort(key=lambda x:x[1], reverse=True)
    print("users by # posts in last 7 days:")
    for sid,count in upairs:
        print("%3d: %s" % (count, sid))

def stalk(sid, depth=1):
    entries = user_from_sid(sid).posts.order_by(Post.posted_date.desc()).limit(depth)
    for e in entries:
        print(e.posted_date)
        print(e.content)
        print "---"
