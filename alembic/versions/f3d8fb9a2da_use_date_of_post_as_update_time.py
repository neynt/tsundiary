"""use date of post as update time

Revision ID: f3d8fb9a2da
Revises: c93e1a6c590
Create Date: 2014-10-09 01:38:54.315388

"""

# revision identifiers, used by Alembic.
revision = 'f3d8fb9a2da'
down_revision = 'c93e1a6c590'

from alembic import op
import sqlalchemy as db


def upgrade():
    op.execute("UPDATE post SET update_time = posted_date WHERE update_time is null")


def downgrade():
    pass
