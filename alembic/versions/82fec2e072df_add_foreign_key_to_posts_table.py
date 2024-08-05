"""add foreign-key to posts table

Revision ID: 82fec2e072df
Revises: 6522cf6265cf
Create Date: 2024-08-05 16:07:58.475373

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "82fec2e072df"
down_revision: Union[str, None] = "6522cf6265cf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("owner_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        "post_user_fk",
        source_table="posts",
        referent_table="users",
        local_cols=["owner_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("post_user_fk", table_name="posts")
    op.drop_column("posts", "owner_id")
