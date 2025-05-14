import enum
from datetime import datetime
from typing import TypedDict
from uuid import UUID

import boto3
import botocore.config
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils.types import StringEncryptedType

from app.conf import settings
from app.core.errors import AppError
from app.core.utils import get_s3_client
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


class ChannelPhoto(BaseModel):
    small_file_id: str | None = None
    small_file_path: str | None = None
    big_file_id: str | None = None
    big_file_path: str | None = None

    def with_signed_urls(self) -> "ChannelPhoto":
        s3_client = get_s3_client()

        def sign_url(file_path: str | None) -> str | None:
            if not file_path:
                return None
            signed_url = s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": settings.STORAGE_BUCKET,
                    "Key": file_path,
                },
                ExpiresIn=60 * 10,
            )
            return signed_url

        return self.model_copy(
            update={
                "small_file_path": sign_url(self.small_file_path),
                "big_file_path": sign_url(self.big_file_path),
            }
        )


class ChannelMetadata(BaseModel):
    id: int
    username: str
    title: str | None = None
    description: str | None = None
    member_count: int | None = None
    photo: ChannelPhoto | None = None

    def with_signed_urls(self) -> "ChannelMetadata":
        return self.model_copy(
            update={"photo": self.photo.with_signed_urls() if self.photo else None}
        )


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


class AgentSummary(TypedDict):
    channel_id: int
    channel_username: str
    channel_title: str
    channel_description: str | None
    channel_profile_generated: str
    content_description: str
    persona_description: str


class TGAgent(RecordModel):
    __tablename__ = "tg_agents"

    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    channel_username: Mapped[str] = string_column(128)
    channel_metadata: Mapped[ChannelMetadata] = mapped_column(
        PydanticJSON(ChannelMetadata), nullable=True
    )
    channel_profile: Mapped[ChannelProfile] = mapped_column(
        PydanticJSON(ChannelProfile), default=dict
    )
    channel_profile_generated: Mapped[str] = mapped_column(
        Text, nullable=False, default="", server_default=""
    )

    bot_permissions: Mapped[BotPermissions] = mapped_column(
        PydanticJSON(BotPermissions, none_as_null=True), nullable=True
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
            self.status == TGAgentStatus.WAITING_CHANNEL_PROFILE
            or self.status == TGAgentStatus.ACTIVE
        )

    def get_summary(self) -> AgentSummary:
        if not self.channel_metadata.title:
            raise AppError("channel_metadata.title is missing", agent_id=self.id)

        if not self.channel_profile.content_description:
            raise AppError(
                "channel_profile.content_description is missing", agent_id=self.id
            )

        if not self.channel_profile.persona_description:
            raise AppError(
                "channel_profile.persona_description is missing", agent_id=self.id
            )
        return {
            "channel_id": self.channel_id,
            "channel_username": self.channel_username,
            "channel_title": self.channel_metadata.title,
            "channel_description": self.channel_metadata.description,
            "channel_profile_generated": self.channel_profile_generated,
            "content_description": self.channel_profile.content_description,
            "persona_description": self.channel_profile.persona_description,
        }


class TGUserBot(RecordModel):
    __tablename__ = "tg_user_bots"

    tg_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    api_token: Mapped[str] = mapped_column(
        StringEncryptedType(key=settings.SECRET_KEY.get_secret_value()),
        nullable=False,
    )
    metadata_: Mapped[BotMetadata] = mapped_column(
        "metadata", PydanticJSON(BotMetadata, none_as_null=True), nullable=True
    )

    # Relationships
    tg_user_id: Mapped[int] = mapped_column(
        ForeignKey("tgbot_tg_users.tg_id", ondelete="RESTRICT"),
    )


class TGAgentJobStatus(str, enum.Enum):
    INITIAL = "initial"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TGAgentJobType(str, enum.Enum):
    POST_GENERATION = "post_generation"
    POST_UPDATE = "post_update"
    CONTENT_DISCOVERY = "content_discovery"
    CONTENT_GENERATION = "content_generation"
    CONTENT_PUBLISHING = "content_publishing"
    CONTENT_ANALYSIS = "content_analysis"


class PostGenerationMetadata(BaseModel):
    user_prompt: str
    notify_message_id: int
    chat_id: int


class PostUpdateMetadata(BaseModel):
    original_message: str
    user_prompt: str
    notify_message_id: int
    chat_id: int
    photo_id: str | None = None


class TGAgentJob(RecordModel):
    __tablename__ = "tg_agent_jobs"

    parent: Mapped[UUID] = mapped_column(
        ForeignKey("tg_agent_jobs.id", ondelete="CASCADE"),
        nullable=True,
    )

    type_: Mapped[TGAgentJobType] = mapped_column(
        "type",
        Enum(
            TGAgentJobType,
            name="tg_agent_job_type",
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
    )

    status: Mapped[TGAgentJobStatus] = mapped_column(
        Enum(
            TGAgentJobStatus,
            name="tg_agent_job_status",
            values_callable=lambda e: [i.value for i in e],
        ),
        default=TGAgentJobStatus.INITIAL,
        nullable=False,
    )
    status_changed_at: Mapped[datetime | None] = mapped_column(default=None)
    status_error: Mapped[ErrorSchema | None] = mapped_column(
        PydanticJSON(ErrorSchema, none_as_null=True), nullable=True
    )
    status_errored_at: Mapped[datetime | None] = mapped_column(default=None)

    metadata_: Mapped[dict[str, str | int]] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    data: Mapped[str] = string_column()

    # Foreign keys
    tg_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("tgbot_tg_users.tg_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    agent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tg_agents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
