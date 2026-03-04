"""initial

Revision ID: 1d45f5d7a013
Revises: 
Create Date: 2026-03-04 00:42:35.600773

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1d45f5d7a013"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "idle_models",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("idle_models_pk")),
    )
    op.create_index(
        op.f("ix_idle_models_user_id"), "idle_models", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_idle_models_user_id"), table_name="idle_models")
    op.drop_table("idle_models")
