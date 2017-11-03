"""add topicss

Revision ID: 2d0f77a13a0d
Revises: 4344458de545
Create Date: 2017-10-25 15:41:24.210795

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d0f77a13a0d'
down_revision = '4344458de545'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('topics', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'topics')
    # ### end Alembic commands ###