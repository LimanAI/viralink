import enum
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils.types import StringEncryptedType

from app.conf import settings
from app.models.base import ErrorSchema, PydanticJSON, RecordModel, string_column


class TGAccountStatus(str, enum.Enum):
    INITIAL = "initial"
    SENT_CODE = "sent_code"
    ACTIVE = "active"
    DISABLED = "disabled"


class TGAccountModel(RecordModel):
    __tablename__ = "tg_accounts"

    phone_number: Mapped[str] = string_column(32)
    api_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, unique=True
    )
    api_hash: Mapped[str] = mapped_column(
        StringEncryptedType(key=settings.SECRET_KEY.get_secret_value()),
        nullable=True,
    )

    phone_code_hash: Mapped[str] = string_column(32)
    session_string = mapped_column(
        StringEncryptedType(key=settings.SECRET_KEY.get_secret_value()),
        nullable=True,
    )
    is_active = Column(Boolean, default=False)
    status: Mapped[TGAccountStatus] = mapped_column(
        Enum(
            TGAccountStatus,
            name="tg_account_status",
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
    )
    status_changed_at: Mapped[datetime | None] = mapped_column(default=None)
    status_error: Mapped[ErrorSchema | None] = mapped_column(
        PydanticJSON(ErrorSchema, none_as_null=True),
        nullable=True,
    )
    status_errored_at: Mapped[datetime | None] = mapped_column(default=None)
    watched_channels_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
