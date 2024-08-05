"""add content column to posts table

Revision ID: cffea418b4a9
Revises: 7021eabdfa11
Create Date: 2024-08-05 15:51:50.451350

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cffea418b4a9"
down_revision: Union[str, None] = "7021eabdfa11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column("posts", "content")
