"""empty message

Revision ID: fa8117cb1c40
Revises: 76b3dde20e08
Create Date: 2022-12-20 15:59:02.219876

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa8117cb1c40'
down_revision = '76b3dde20e08'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('isverified', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'isverified')
    # ### end Alembic commands ###
