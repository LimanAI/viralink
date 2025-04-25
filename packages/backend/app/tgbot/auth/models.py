from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import PostgresUUID, RecordModel, string_column


class TGUserModel(RecordModel):
    __tablename__ = "tgbot_tg_users"

    tg_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, unique=True, index=True
    )
    username: Mapped[str] = string_column(64)
    first_name: Mapped[str] = string_column(64)
    last_name: Mapped[str] = string_column(64)
    phone: Mapped[str] = string_column(64)
    language_code: Mapped[str] = string_column(8)

    is_bot: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_blocked: Mapped[bool] = mapped_column(nullable=False, default=False)

    user = mapped_column(PostgresUUID, ForeignKey("auth_users.id"), nullable=False)
