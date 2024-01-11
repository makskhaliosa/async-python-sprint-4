"""03_add_user_model_user_foreign_key

Revision ID: eb9469f870f1
Revises: 899393743856
Create Date: 2023-12-23 17:10:47.257029

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb9469f870f1'
down_revision: Union[str, None] = '899393743856'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.add_column('url', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'url', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'url', type_='foreignkey')
    op.drop_column('url', 'user_id')
    op.drop_table('user')
    # ### end Alembic commands ###