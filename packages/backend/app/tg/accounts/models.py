import enum
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, Enum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils.types import StringEncryptedType

from app.conf import settings
from app.models.base import RecordModel, string_column


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
            name="tgbot_tg_account_status",
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
    )
    status_changed_at: Mapped[datetime | None] = mapped_column(default=None)
    status_error: Mapped[dict[str, str] | None] = mapped_column(
        JSONB(none_as_null=True),  # type: ignore[no-untyped-call]
        nullable=True,
    )
    status_errored_at: Mapped[datetime | None] = mapped_column(default=None)
