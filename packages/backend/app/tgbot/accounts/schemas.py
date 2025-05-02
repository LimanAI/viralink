from uuid import UUID

from pydantic import BaseModel

from app.tgbot.accounts.models import TGAccountStatus


class CreateAccountRequest(BaseModel):
    phone_number: str
    api_id: int
    api_hash: str


class CodeRequest(BaseModel):
    phone_number: str
    api_id: int


class SignInRequest(BaseModel):
    api_id: int
    code: int
    password: str | None = None


class TGAccount(BaseModel):
    id: UUID
    status: TGAccountStatus
