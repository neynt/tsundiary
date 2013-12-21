from tsundiary import User, Post, db

def delete_user(sid):
    Post.query.filter_by(user_sid=sid).delete()
    User.query.filter_by(sid=sid).delete()
    db.session.commit()

def user_from_sid(sid):
    return User.query.filter_by(sid=sid).first()
