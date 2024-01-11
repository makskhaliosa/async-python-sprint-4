"""01_initial_url_client_connection

Revision ID: 73c03306d384
Revises: 
Create Date: 2023-12-17 16:51:13.290635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73c03306d384'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('url',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('original_url', sa.String(), nullable=False),
    sa.Column('short_url', sa.String(), nullable=True),
    sa.Column('call_number', sa.Integer(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('original_url'),
    sa.UniqueConstraint('short_url')
    )
    op.create_index(op.f('ix_url_created'), 'url', ['created'], unique=False)
    op.create_table('client_connection',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('client_info', sa.String(), nullable=True),
    sa.Column('url_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['url_id'], ['url.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('client_connection')
    op.drop_index(op.f('ix_url_created'), table_name='url')
    op.drop_table('url')
    # ### end Alembic commands ###