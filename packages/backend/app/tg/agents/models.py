import enum
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import BigInteger, Enum, ForeignKey
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


class TGAgentStatus(str, enum.Enum):
    INITIAL = "initial"
    WAITING_BOT_ATTACH = "waiting_bot_attach"
    WAITING_BOT_ACCESS = "waiting_bot_access"
    REQUIRES_CHANNEL_PROFILE = "requires_channel_profile"
    ACTIVE = "active"
    DISABLED = "disabled"
    DISABLED_NO_CREDIT = "disabled_no_credit"


class ChannelMetadata(BaseModel):
    title: str | None = None
    handle: str | None = None
    description: str | None = None


class ChannelProfile(BaseModel):
    persona_description: str | None = None
    content_description: str | None = None


class TGAgent(RecordModel):
    __tablename__ = "tg_agents"

    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    channel_link: Mapped[str] = string_column(128)
    channel_metadata: Mapped[ChannelMetadata] = mapped_column(
        PydanticJSON(ChannelMetadata), default=dict
    )
    channel_profile: Mapped[ChannelProfile] = mapped_column(
        PydanticJSON(ChannelProfile), default=dict
    )

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

    # Relationships
    tg_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("tgbot_tg_users.tg_id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    user_bot_id: Mapped[int | None] = mapped_column(
        ForeignKey("tg_user_bots.tg_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )


class TGUserBot(TimestampModel):
    __tablename__ = "tg_user_bots"

    tg_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    api_key: Mapped[str] = mapped_column(
        StringEncryptedType(key=settings.SECRET_KEY.get_secret_value()),
        nullable=False,
    )

    # Relationships
    tg_user_id: Mapped[int] = mapped_column(
        ForeignKey("tgbot_tg_users.tg_id", ondelete="RESTRICT"),
    )
