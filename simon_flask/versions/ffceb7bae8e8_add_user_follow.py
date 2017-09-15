"""add user follow

Revision ID: ffceb7bae8e8
Revises: 42ea0360a67f
Create Date: 2017-09-01 20:53:36.885292

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffceb7bae8e8'
down_revision = '42ea0360a67f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('follows',
    sa.Column('follow_from', sa.Integer(), nullable=False),
    sa.Column('follow_to', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('follow_from', 'follow_to')
    )
    op.create_index(op.f('ix_follows_follow_from'), 'follows', ['follow_from'], unique=False)
    op.create_index(op.f('ix_follows_follow_to'), 'follows', ['follow_to'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_follows_follow_to'), table_name='follows')
    op.drop_index(op.f('ix_follows_follow_from'), table_name='follows')
    op.drop_table('follows')
    # ### end Alembic commands ###