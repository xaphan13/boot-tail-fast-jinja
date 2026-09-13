"""Migrate blog_user to fastapi-users fields.

Revision ID: a1c2d3e4f5a6
Revises: b59cbdf15878
Create Date: 2026-09-13 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1c2d3e4f5a6"
down_revision: Union[str, None] = "b59cbdf15878"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_HASHED_PASSWORD_LENGTH = 1024
_LEGACY_PASSWORD_LENGTH = 60


def upgrade() -> None:
    """Rename the legacy hash column and add fastapi-users auth flags."""
    with op.batch_alter_table("blog_user", recreate="auto") as batch_op:
        batch_op.alter_column(
            "password",
            existing_type=sa.String(length=_LEGACY_PASSWORD_LENGTH),
            type_=sa.String(length=_HASHED_PASSWORD_LENGTH),
            existing_nullable=False,
            new_column_name="hashed_password",
        )
        batch_op.add_column(
            sa.Column(
                "is_active",
                sa.Boolean(),
                server_default=sa.true(),
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "is_superuser",
                sa.Boolean(),
                server_default=sa.false(),
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "is_verified",
                sa.Boolean(),
                server_default=sa.false(),
                nullable=False,
            )
        )


def downgrade() -> None:
    """Restore the legacy password column without deleting blog users."""
    with op.batch_alter_table("blog_user", recreate="auto") as batch_op:
        batch_op.drop_column("is_verified")
        batch_op.drop_column("is_superuser")
        batch_op.drop_column("is_active")
        batch_op.alter_column(
            "hashed_password",
            existing_type=sa.String(length=_HASHED_PASSWORD_LENGTH),
            type_=sa.String(length=_LEGACY_PASSWORD_LENGTH),
            existing_nullable=False,
            new_column_name="password",
        )
