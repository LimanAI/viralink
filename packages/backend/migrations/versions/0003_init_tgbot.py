"""init_tgbot

Revision ID: 0003
Revises: 0002
Create Date: 2025-05-13 13:57:23.759617

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
import sqlalchemy_utils.types
from alembic import op
from sqlalchemy.dialects import postgresql

import app.models.base
from app.tg.agents.models import (
    BotMetadata,
    BotPermissions,
    ChannelMetadata,
    ChannelProfile,
)

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum(
        "initial", "in_progress", "completed", "failed", name="tg_agent_job_status"
    ).create(op.get_bind())  # type: ignore[no-untyped-call]
    sa.Enum(
        "post_generation",
        "post_update",
        "content_discovery",
        "content_generation",
        "content_publishing",
        "content_analysis",
        name="tg_agent_job_type",
    ).create(op.get_bind())  # type: ignore[no-untyped-call]
    sa.Enum(
        "initial",
        "waiting_bot_attach",
        "waiting_bot_access",
        "waiting_channel_profile",
        "active",
        "disabled",
        "disabled_no_credit",
        name="tg_agent_status",
    ).create(op.get_bind())  # type: ignore[no-untyped-call]
    op.create_table(
        "tgbot_tg_invite_codes",
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("uses_left", sa.Integer(), nullable=False),
        sa.Column("is_created_by_admin", sa.Boolean(), nullable=False),
        sa.Column("tg_user_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["tg_user_id"],
            ["tgbot_tg_users.tg_id"],
            name=op.f("fk_tgbot_tg_invite_codes_tgbot_tg_users__tg_user_id"),
        ),
        sa.PrimaryKeyConstraint("code", name=op.f("pk_tgbot_tg_invite_codes")),
    )
    op.create_index(
        op.f("ix_tgbot_tg_invite_codes_tg_user_id"),
        "tgbot_tg_invite_codes",
        ["tg_user_id"],
        unique=False,
    )
    op.create_table(
        "tg_user_bots",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tg_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "api_token",
            sqlalchemy_utils.types.encrypted.encrypted_type.StringEncryptedType(),
            nullable=False,
        ),
        sa.Column(
            "metadata",
            app.models.base.PydanticJSON(
                BotMetadata, none_as_null=True, astext_type=sa.Text()
            ),
            nullable=True,
        ),
        sa.Column("tg_user_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["tg_user_id"],
            ["tgbot_tg_users.tg_id"],
            name=op.f("fk_tg_user_bots_tgbot_tg_users__tg_user_id"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tg_user_bots")),
    )
    op.create_index(
        op.f("ix_tg_user_bots_tg_id"), "tg_user_bots", ["tg_id"], unique=False
    )
    op.create_table(
        "tg_agents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=True),
        sa.Column("channel_username", sa.String(length=128), nullable=False),
        sa.Column(
            "channel_metadata",
            app.models.base.PydanticJSON(ChannelMetadata, astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "channel_profile",
            app.models.base.PydanticJSON(ChannelProfile, astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "bot_permissions",
            app.models.base.PydanticJSON(
                BotPermissions, none_as_null=True, astext_type=sa.Text()
            ),
            nullable=True,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "initial",
                "waiting_bot_attach",
                "waiting_bot_access",
                "waiting_channel_profile",
                "active",
                "disabled",
                "disabled_no_credit",
                name="tg_agent_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("status_changed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "status_error",
            app.models.base.PydanticJSON(
                app.models.base.ErrorSchema, none_as_null=True, astext_type=sa.Text()
            ),
            nullable=True,
        ),
        sa.Column("status_errored_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("tg_user_id", sa.BigInteger(), nullable=True),
        sa.Column("user_bot_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["tg_user_id"],
            ["tgbot_tg_users.tg_id"],
            name=op.f("fk_tg_agents_tgbot_tg_users__tg_user_id"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_bot_id"],
            ["tg_user_bots.id"],
            name=op.f("fk_tg_agents_tg_user_bots__user_bot_id"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tg_agents")),
    )
    op.create_index(
        op.f("ix_tg_agents_tg_user_id"), "tg_agents", ["tg_user_id"], unique=False
    )
    op.create_index(
        op.f("ix_tg_agents_user_bot_id"), "tg_agents", ["user_bot_id"], unique=False
    )
    op.create_table(
        "tg_agent_jobs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("parent", sa.UUID(), nullable=True),
        sa.Column(
            "type",
            postgresql.ENUM(
                "post_generation",
                "post_update",
                "content_discovery",
                "content_generation",
                "content_publishing",
                "content_analysis",
                name="tg_agent_job_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "initial",
                "in_progress",
                "completed",
                "failed",
                name="tg_agent_job_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("status_changed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "status_error",
            app.models.base.PydanticJSON(
                app.models.base.ErrorSchema, none_as_null=True, astext_type=sa.Text()
            ),
            nullable=True,
        ),
        sa.Column("status_errored_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "metadata_",
            postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("data", sa.String(), nullable=False),
        sa.Column("tg_user_id", sa.BigInteger(), nullable=True),
        sa.Column("agent_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["tg_agents.id"],
            name=op.f("fk_tg_agent_jobs_tg_agents__agent_id"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["parent"],
            ["tg_agent_jobs.id"],
            name=op.f("fk_tg_agent_jobs_tg_agent_jobs__parent"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tg_user_id"],
            ["tgbot_tg_users.tg_id"],
            name=op.f("fk_tg_agent_jobs_tgbot_tg_users__tg_user_id"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tg_agent_jobs")),
    )
    op.create_index(
        op.f("ix_tg_agent_jobs_agent_id"), "tg_agent_jobs", ["agent_id"], unique=False
    )
    op.create_index(
        op.f("ix_tg_agent_jobs_tg_user_id"),
        "tg_agent_jobs",
        ["tg_user_id"],
        unique=False,
    )
    op.add_column("tgbot_tg_users", sa.Column("is_admin", sa.Boolean(), nullable=False))
    op.add_column(
        "tgbot_tg_users", sa.Column("invite_code", sa.String(), nullable=True)
    )
    op.create_foreign_key(
        op.f("fk_tgbot_tg_users_tgbot_tg_invite_codes__invite_code"),
        "tgbot_tg_users",
        "tgbot_tg_invite_codes",
        ["invite_code"],
        ["code"],
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        op.f("fk_tgbot_tg_users_tgbot_tg_invite_codes__invite_code"),
        "tgbot_tg_users",
        type_="foreignkey",
    )
    op.drop_column("tgbot_tg_users", "invite_code")
    op.drop_column("tgbot_tg_users", "is_admin")
    op.drop_index(op.f("ix_tg_agent_jobs_tg_user_id"), table_name="tg_agent_jobs")
    op.drop_index(op.f("ix_tg_agent_jobs_agent_id"), table_name="tg_agent_jobs")
    op.drop_table("tg_agent_jobs")
    op.drop_index(op.f("ix_tg_agents_user_bot_id"), table_name="tg_agents")
    op.drop_index(op.f("ix_tg_agents_tg_user_id"), table_name="tg_agents")
    op.drop_table("tg_agents")
    op.drop_index(op.f("ix_tg_user_bots_tg_id"), table_name="tg_user_bots")
    op.drop_table("tg_user_bots")
    op.drop_index(
        op.f("ix_tgbot_tg_invite_codes_tg_user_id"), table_name="tgbot_tg_invite_codes"
    )
    op.drop_table("tgbot_tg_invite_codes")
    sa.Enum(
        "initial",
        "waiting_bot_attach",
        "waiting_bot_access",
        "waiting_channel_profile",
        "active",
        "disabled",
        "disabled_no_credit",
        name="tg_agent_status",
    ).drop(op.get_bind())  # type: ignore[no-untyped-call]
    sa.Enum(
        "post_generation",
        "post_update",
        "content_discovery",
        "content_generation",
        "content_publishing",
        "content_analysis",
        name="tg_agent_job_type",
    ).drop(op.get_bind())  # type: ignore[no-untyped-call]
    sa.Enum(
        "initial", "in_progress", "completed", "failed", name="tg_agent_job_status"
    ).drop(op.get_bind())  # type: ignore[no-untyped-call]
    # ### end Alembic commands ###
