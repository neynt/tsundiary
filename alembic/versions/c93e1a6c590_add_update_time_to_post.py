"""add update_time to post

Revision ID: c93e1a6c590
Revises: 2c2a4dfdb616
Create Date: 2014-10-09 00:58:00.352701

"""

# revision identifiers, used by Alembic.
revision = 'c93e1a6c590'
down_revision = '2c2a4dfdb616'

from alembic import op
import sqlalchemy as db


def upgrade():
    op.add_column('post',
        db.Column('update_time', db.DateTime)
    )


def downgrade():
    op.drop_column('post', 'update_time')
