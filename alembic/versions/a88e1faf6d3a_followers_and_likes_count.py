"""followers_and_likes_count

Revision ID: a88e1faf6d3a
Revises: 82dd9e59a918
Create Date: 2024-10-09 15:46:38.930523

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a88e1faf6d3a'
down_revision: Union[str, None] = '82dd9e59a918'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('likes', sa.Integer(), server_default='0', nullable=False))
    op.add_column('posts', sa.Column('comments', sa.Integer(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('followers', sa.Integer(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('followings', sa.Integer(), server_default='0', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'followings')
    op.drop_column('users', 'followers')
    op.drop_column('posts', 'comments')
    op.drop_column('posts', 'likes')
    # ### end Alembic commands ###