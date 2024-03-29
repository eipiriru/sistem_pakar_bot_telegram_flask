"""empty message

Revision ID: 02b65d36eca3
Revises: 
Create Date: 2022-08-30 23:19:16.338539

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02b65d36eca3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gejala',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('kode', sa.String(length=5), nullable=True),
    sa.Column('gejala', sa.String(length=50), nullable=True),
    sa.Column('deskripsi', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('kode')
    )
    op.create_table('penyakit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('kode', sa.String(length=5), nullable=True),
    sa.Column('penyakit', sa.String(length=50), nullable=True),
    sa.Column('deskripsi', sa.Text(), nullable=True),
    sa.Column('penanganan', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('kode')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('type_user', sa.Enum('admin', 'pakar', name='type'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('relasi',
    sa.Column('penyakit_id', sa.Integer(), nullable=True),
    sa.Column('gejala_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['gejala_id'], ['gejala.id'], ),
    sa.ForeignKeyConstraint(['penyakit_id'], ['penyakit.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('relasi')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_table('user')
    op.drop_table('penyakit')
    op.drop_table('gejala')
    # ### end Alembic commands ###
