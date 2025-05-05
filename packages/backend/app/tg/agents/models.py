import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, Enum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils.types import StringEncryptedType

from app.conf import settings
from app.models.base import (
    ErrorSchema,
    PydanticJSON,
    RecordModel,
    TimestampModel,
    string_column,
)


class TGChannel(TimestampModel):
    __tablename__ = "tg_channels"

    tg_channel_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class TGAgentStatus(str, enum.Enum):
    INITIAL = "initial"
    CHANNEL_ANALYSIS = "channel_analysis"
    POST_GENERATION = "post_generation"
    ACTIVE = "active"
    DISABLED = "disabled"


class TGAgent(RecordModel):
    __tablename__ = "tg_agents"

    status: Mapped[TGAgentStatus] = mapped_column(
        Enum(
            TGAgentStatus,
            name="tg_agent_status",
            values_callable=lambda e: [i.value for i in e],
        ),
        default=TGAgentStatus.INITIAL,
        nullable=False,
    )
    status_changed_at: Mapped[datetime | None] = mapped_column(default=None)
    status_error: Mapped[ErrorSchema | None] = mapped_column(
        PydanticJSON(ErrorSchema, none_as_null=True), nullable=True
    )
    status_errored_at: Mapped[datetime | None] = mapped_column(default=None)

    tg_channel_id: Mapped[int] = mapped_column(
        ForeignKey("tg_channels.tg_channel_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Relationships
    tg_account_id: Mapped[UUID] = mapped_column(
        ForeignKey("tg_accounts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("auth_users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    tg_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("tgbot_tg_users.tg_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )


class TGChannelConnectionStatus(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class TGChannelConnection(RecordModel):
    __tablename__ = "tg_channel_connections"

    tg_account_id: Mapped[UUID] = mapped_column(
        ForeignKey("tg_accounts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    tg_channel_id: Mapped[int] = mapped_column(
        ForeignKey("tg_channels.tg_channel_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    access_hash: Mapped[int] = mapped_column(
        StringEncryptedType(key=settings.SECRET_KEY.get_secret_value()),
        nullable=False,
    )

    status: Mapped[TGChannelConnectionStatus] = mapped_column(
        Enum(
            TGChannelConnectionStatus,
            name="tg_channel_connection_status",
            values_callable=lambda e: [i.value for i in e],
        ),
        default=TGChannelConnectionStatus.CONNECTED,
        nullable=False,
    )
    status_changed_at: Mapped[datetime | None] = mapped_column(default=None)
    status_error: Mapped[ErrorSchema | None] = mapped_column(
        PydanticJSON(ErrorSchema, none_as_null=True), nullable=True
    )
    status_errored_at: Mapped[datetime | None] = mapped_column(default=None)

    __table_args__ = (
        Index(
            "ix_tg_channel_watchers_channel_account", "tg_channel_id", "tg_account_id"
        ),
    )


class TGChannelProfile(RecordModel):
    __tablename__ = "tg_channel_profiles"

    tg_agent_id: Mapped[UUID] = mapped_column(
        ForeignKey("tg_agents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tg_channel_id: Mapped[int] = mapped_column(
        ForeignKey("tg_channels.tg_channel_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
