from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.tg.agents.models import (
    BotMetadata,
    ChannelMetadata,
    ChannelProfile,
    TGAgentStatus,
)


class TGUserBot(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime

    metadata: BotMetadata | None = Field(default=None, alias="metadata_")


class TGAgent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime

    status: TGAgentStatus
    status_changed_at: datetime | None = None

    channel_id: int | None = None
    channel_username: str | None = None
    channel_metadata: ChannelMetadata | None = None
    channel_profile: ChannelProfile | None = None

    user_bot: TGUserBot | None = None

    def with_signed_urls(self) -> "TGAgent":
        return self.model_copy(
            update={
                "channel_metadata": self.channel_metadata.with_signed_urls()
                if self.channel_metadata
                else None,
            }
        )


class CreateTGAgentRequest(BaseModel):
    channel_username: str


class UpdateChannelProfileRequest(BaseModel):
    content_description: str | None = None
    persona_description: str | None = None


class AddTGBotRequest(BaseModel):
    bot_token: str


class LinkTGBotRequest(BaseModel):
    bot_id: UUID
