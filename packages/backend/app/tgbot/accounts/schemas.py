from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.tgbot.accounts.models import TGAccountStatus


class CreateAccountRequest(BaseModel):
    phone_number: str
    api_id: int
    api_hash: str


class CodeRequest(BaseModel):
    account_id: UUID
    phone_number: str


class SignInRequest(BaseModel):
    account_id: UUID
    code: int
    password: str | None = None


class TGAccount(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: TGAccountStatus
