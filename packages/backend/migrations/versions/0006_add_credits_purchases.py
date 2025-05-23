"""add_credits_purchases

Revision ID: 0006
Revises: 0005
Create Date: 2025-05-16 15:32:48.857098

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
import sqlalchemy_utils.types
from alembic import op
from sqlalchemy.dialects import postgresql

import app.models.base
from app.tg.credits.models import StarsPurchaseMetadata

# revision identifiers, used by Alembic.
revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum(
        "initial", "confirmed", "completed", name="tg_user_credits_purchase_status"
    ).create(op.get_bind())  # type: ignore[no-untyped-call]
    op.create_table(
        "tg_user_credits_purchases",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("credits_amount", sa.BigInteger(), nullable=False),
        sa.Column("package_name", sa.String(), nullable=False),
        sa.Column(
            "metadata",
            app.models.base.PydanticJSON(
                StarsPurchaseMetadata, none_as_null=True, astext_type=sa.Text()
            ),
            nullable=True,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "initial",
                "confirmed",
                "completed",
                name="tg_user_credits_purchase_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("tg_user_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["tg_user_id"],
            ["tgbot_tg_users.tg_id"],
            name=op.f("fk_tg_user_credits_purchases_tgbot_tg_users__tg_user_id"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tg_user_credits_purchases")),
    )
    op.create_index(
        op.f("ix_tg_user_credits_purchases_tg_user_id"),
        "tg_user_credits_purchases",
        ["tg_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_tg_user_credits_transactions__hanging_purchases",
        "tg_user_credits_purchases",
        ["status", "created_at"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "ix_tg_user_credits_transactions__hanging_purchases",
        table_name="tg_user_credits_purchases",
    )
    op.drop_index(
        op.f("ix_tg_user_credits_purchases_tg_user_id"),
        table_name="tg_user_credits_purchases",
    )
    op.drop_table("tg_user_credits_purchases")
    sa.Enum(
        "initial", "confirmed", "completed", name="tg_user_credits_purchase_status"
    ).drop(op.get_bind())  # type: ignore[no-untyped-call]
    # ### end Alembic commands ###
