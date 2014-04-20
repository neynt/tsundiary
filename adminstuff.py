from tsundiary import User, Post, db

def delete_user(sid):
    Post.query.filter_by(user_sid=sid).delete()
    User.query.filter_by(sid=sid).delete()
    db.session.commit()

def user_from_sid(sid):
    return User.query.filter_by(sid=sid).first()

def stalk(sid, depth=1):
    entries = user_from_sid(sid).posts.order_by(Post.posted_date.desc()).limit(depth)
    for e in entries:
        print(e.posted_date)
        print(e.content)
        print "---"
