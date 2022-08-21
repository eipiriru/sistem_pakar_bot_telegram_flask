"""change kolom in tabel user

Revision ID: 18564ff8c8f5
Revises: b5f132de4d58
Create Date: 2022-08-18 16:43:55.131550

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18564ff8c8f5'
down_revision = 'b5f132de4d58'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('user_type', sa.Enum('admin', 'pakar', name='Tipe Pengguna'), nullable=True))
    op.drop_index('ix_user_email', table_name='user')
    op.drop_column('user', 'email')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('email', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.create_index('ix_user_email', 'user', ['email'], unique=False)
    op.drop_column('user', 'user_type')
    # ### end Alembic commands ###
