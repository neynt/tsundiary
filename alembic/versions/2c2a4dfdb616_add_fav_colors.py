"""add fav colors

Revision ID: 2c2a4dfdb616
Revises: 3fc4fca84eb8
Create Date: 2014-10-08 23:39:47.639889

"""

# revision identifiers, used by Alembic.
revision = '2c2a4dfdb616'
down_revision = '3fc4fca84eb8'

from alembic import op
import sqlalchemy as db


def upgrade():
    op.add_column('user',
        db.Column('color', db.String)
    )
    pass


def downgrade():
    op.drop_column('user', 'color')
    pass
