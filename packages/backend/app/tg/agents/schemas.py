from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.tg.agents.models import TGAgentStatus


class TGAgentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime

    status: TGAgentStatus
    status_changed_at: datetime | None = None

    channel_id: int | None = None


class CreateTGAgentRequest(BaseModel):
    channel_link: str
