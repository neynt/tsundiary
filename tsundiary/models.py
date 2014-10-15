import uuid
import hashlib
from datetime import datetime, date, timedelta
from flask.ext.sqlalchemy import SQLAlchemy
from tsundiary import app
from tsundiary.utils import uidify

db = SQLAlchemy(app)

##############
# ORM objects

class User(db.Model):
    """ A tsundiary user and all their settings. """
    __tablename__ = 'user'
    sid = db.Column(db.String, primary_key=True, index=True, unique=True)
    name = db.Column(db.String, index=True, unique=True)
    passhash = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    invite_key = db.Column(db.String)
    join_time = db.Column(db.DateTime, index=True)
    num_entries = db.Column(db.Integer, index=True)
    combo = db.Column(db.Integer, index=True)
    secret_days = db.Column(db.Integer)
    publicity = db.Column(db.Integer)
    theme = db.Column(db.String)
    color = db.Column(db.String)
    latest_post_date = db.Column(db.Date, index=True)

    def verify_password(self, password):
        """ Checks whether a user's password is equal to the given string."""
        salt = self.passhash[:32].encode('utf-8')
        pas = hashlib.sha512(salt + password.encode('utf-8'))
        pash = pas.hexdigest().encode('utf-8')
        return salt + pash == self.passhash

    def set_password(self, password):
        salt = uuid.uuid4().hex.encode('utf-8')
        pas = hashlib.sha512(salt + password.encode('utf-8'))
        pash = pas.hexdigest().encode('utf-8')
        self.passhash = salt + pash

    def __init__(self, name, password, email=None, invite_key=""):
        self.sid = uidify(name)
        self.name = name
        self.set_password(password)
        self.email = email
        self.invite_key = invite_key
        self.join_time = datetime.now()
        self.num_entries = 0
        self.combo = 0
        self.secret_days = 0
        # publicity
        # 0: completely hidden1: anyone with the link  2. link in user list
        self.publicity = 2
        self.theme = 'classic'
        self.color = '0,100,100'

    def __repr__(self):
        return '<User %r>' % self.name

class Post(db.Model):
    """ A user's post. """
    __tablename__ = 'post'
    user_sid = db.Column(db.String,
                         db.ForeignKey('user.sid'),
                         primary_key=True,
                         index=True)
    posted_date = db.Column(db.Date, primary_key=True, index=True)
    update_time = db.Column(db.DateTime)
    content = db.Column(db.String)
    user = db.relationship('User',
                           backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, user_sid, content, posted_date):
        self.user_sid = user_sid
        self.posted_date = posted_date
        self.content = content

    def __repr__(self):
        return '<Post by %r on %r>' % (self.user_sid, self.posted_date)

def init_db():
    db.drop_all()
    db.create_all()

def populate_db():
    admin = User("admin", "cake")
    bob = User("bob", "yolo")
    admin_1 = Post(admin.sid, "yolosshiku", date.today())
    admin_2 = Post(admin.sid, "good dame", date.today()-timedelta(days=1))
    admin_3 = Post(admin.sid, "hardy har", date.today()-timedelta(days=2))
    admin_4 = Post(admin.sid, "i cannot belief", date.today()-timedelta(days=7))
    admin_5 = Post(admin.sid, "i'm alive", date.today()-timedelta(days=365))
    bob_1 = Post(bob.sid, "what goodness", date.today())
    bob_2 = Post(bob.sid, "what cruelty", date.today()-timedelta(days=1))
    db.session.add(admin)
    db.session.add(admin_1)
    db.session.add(admin_2)
    db.session.add(admin_3)
    db.session.add(admin_4)
    db.session.add(admin_5)
    db.session.add(bob)
    db.session.add(bob_1)
    db.session.add(bob_2)
    db.session.commit()
