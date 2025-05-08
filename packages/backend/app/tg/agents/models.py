import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import BigInteger, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils.types import StringEncryptedType

from app.conf import settings
from app.models.base import (
    ErrorSchema,
    PydanticJSON,
    RecordModel,
    string_column,
)


class TGAgentStatus(str, enum.Enum):
    INITIAL = "initial"
    WAITING_BOT_ATTACH = "waiting_bot_attach"
    WAITING_BOT_ACCESS = "waiting_bot_access"
    WAITING_CHANNEL_PROFILE = "waiting_channel_profile"
    ACTIVE = "active"
    DISABLED = "disabled"
    DISABLED_NO_CREDIT = "disabled_no_credit"


class ChannelMetadata(BaseModel):
    username: str | None = None
    title: str | None = None
    description: str | None = None


class ChannelProfile(BaseModel):
    content_description: str | None = None
    persona_description: str | None = None


class BotMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str | None = None
    first_name: str | None = None
    description: str | None = None


class BotPermissions(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    is_admin: bool = False

    can_manage_voice_chats: bool = False
    can_be_edited: bool = False
    can_change_info: bool = False
    can_delete_messages: bool = False
    can_delete_stories: bool = False
    can_edit_stories: bool = False
    can_invite_users: bool = False
    can_manage_chat: bool = False
    can_manage_topics: bool = False
    can_manage_video_chats: bool = False
    can_pin_messages: bool = False
    can_post_stories: bool = False
    can_promote_members: bool = False
    can_restrict_members: bool = False
    is_anonymous: bool = False


class TGAgent(RecordModel):
    __tablename__ = "tg_agents"

    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    channel_username: Mapped[str] = string_column(128)
    channel_metadata: Mapped[ChannelMetadata] = mapped_column(
        PydanticJSON(ChannelMetadata), default=dict
    )
    channel_profile: Mapped[ChannelProfile] = mapped_column(
        PydanticJSON(ChannelProfile), default=dict
    )

    bot_permissions: Mapped[BotPermissions] = mapped_column(
        PydanticJSON(BotPermissions), none_as_null=True, nullable=True
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
        PydanticJSON(ErrorSchema), none_as_null=True, nullable=True
    )
    status_errored_at: Mapped[datetime | None] = mapped_column(default=None)

    # Foreign keys
    tg_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("tgbot_tg_users.tg_id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    user_bot_id: Mapped[int | None] = mapped_column(
        ForeignKey("tg_user_bots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    user_bot: Mapped["TGUserBot"] = relationship(
        "TGUserBot",
        lazy="noload",
    )

    def bot_is_connected(self) -> bool:
        return self.user_bot is not None and (
            self.status == TGAgentStatus.REQUIRES_CHANNEL_PROFILE
            or self.status == TGAgentStatus.ACTIVE
        )


class TGUserBot(RecordModel):
    __tablename__ = "tg_user_bots"

    tg_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    api_token: Mapped[str] = mapped_column(
        StringEncryptedType(key=settings.SECRET_KEY.get_secret_value()),
        nullable=False,
    )
    metadata_: Mapped[BotMetadata] = mapped_column(
        "metadata", PydanticJSON(BotMetadata), none_as_null=True, nullable=True
    )

    # Relationships
    tg_user_id: Mapped[int] = mapped_column(
        ForeignKey("tgbot_tg_users.tg_id", ondelete="RESTRICT"),
    )
