"""empty message

Revision ID: c692246eb58a
Revises: 61694e751fab
Create Date: 2017-02-25 23:59:33.632167

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c692246eb58a'
down_revision = '61694e751fab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('car', sa.Column('last_seen', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('car', 'last_seen')
    # ### end Alembic commands ###
