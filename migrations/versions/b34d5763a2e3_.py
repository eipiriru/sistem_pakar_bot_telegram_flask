"""empty message

Revision ID: b34d5763a2e3
Revises: 890836f68dbb
Create Date: 2022-08-30 22:59:04.850318

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b34d5763a2e3'
down_revision = '890836f68dbb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bot_config')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bot_config',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('token', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('url', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='bot_config_pkey')
    )
    # ### end Alembic commands ###
