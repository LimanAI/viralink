from pydantic import EmailStr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils.types import PasswordType

from app.models.base import RecordModel, string_column


class UserModel(RecordModel):
    __tablename__ = "auth_users"

    email: Mapped[EmailStr] = mapped_column(unique=True, index=True, nullable=True)
    username: Mapped[str] = string_column(64)
    fullname: Mapped[str] = string_column(128)
    password: Mapped[str | None] = mapped_column(
        PasswordType(
            schemes=["pbkdf2_sha512"],
            pdbkdf2_sha512__salt_size=16,
            pdbkdf2_sha512__rounds=25000,
        ),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
