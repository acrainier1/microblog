"""kanji data

Revision ID: f39c5279cac6
Revises: 95fb738ed16e
Create Date: 2020-08-20 21:50:56.578494

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f39c5279cac6'
down_revision = '95fb738ed16e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('kanjidata')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('kanjidata',
    sa.Column('Order1', sa.INTEGER(), nullable=True),
    sa.Column('Frequency1', sa.INTEGER(), nullable=True),
    sa.Column('Kanji1', sa.TEXT(), nullable=True),
    sa.Column('Type1', sa.TEXT(), nullable=True),
    sa.Column('Meaning1', sa.TEXT(), nullable=True),
    sa.Column('Meaning2', sa.TEXT(), nullable=True),
    sa.Column('Meaning3', sa.TEXT(), nullable=True),
    sa.Column('Radical1', sa.TEXT(), nullable=True),
    sa.Column('Radical2', sa.TEXT(), nullable=True),
    sa.Column('Radical3', sa.TEXT(), nullable=True),
    sa.Column('Radical4', sa.TEXT(), nullable=True),
    sa.Column('Onyomi\xa0Reading1', sa.TEXT(), nullable=True),
    sa.Column('Onyomi\xa0Reading2', sa.TEXT(), nullable=True),
    sa.Column('Kunyomi Reading1', sa.TEXT(), nullable=True),
    sa.Column('Kunyomi Reading2', sa.TEXT(), nullable=True),
    sa.Column('Mnemonic', sa.TEXT(), nullable=True),
    sa.Column('Notes', sa.TEXT(), nullable=True)
    )
    # ### end Alembic commands ###