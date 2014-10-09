"""init 2014-10-08

Revision ID: 3fc4fca84eb8
Revises: None
Create Date: 2014-10-08 23:21:08.562968

"""

# revision identifiers, used by Alembic.
revision = '3fc4fca84eb8'
down_revision = None

from alembic import op
import sqlalchemy as db

def upgrade():
    op.create_table('user',
        db.Column('sid', db.String, primary_key=True, index=True, unique=True),
        db.Column('name', db.String, index=True, unique=True),
        db.Column('passhash', db.String),
        db.Column('email', db.String, unique=True),
        db.Column('invite_key', db.String),
        db.Column('join_time', db.DateTime, index=True),
        db.Column('num_entries', db.Integer, index=True),
        db.Column('combo', db.Integer, index=True),
        db.Column('secret_days', db.Integer),
        db.Column('publicity', db.Integer),
        db.Column('theme', db.String),
        db.Column('latest_post_date', db.Date, index=True),
    )
    op.create_table('post',
        db.Column(
            'user_sid', db.String,
            db.ForeignKey('user.sid'),
            primary_key=True,
            index=True,
        ),
        db.Column('posted_date', db.Date, primary_key=True, index=True),
        db.Column('content', db.String),
        user = db.relationship('User',
            backref=db.backref('posts', lazy='dynamic')),
    )

def downgrade():
    op.drop_table('user')
    op.drop_table('post')
    pass
