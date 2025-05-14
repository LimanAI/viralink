import enum

from sqlalchemy import BigInteger, CheckConstraint, Enum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import RecordModel


class CreditsTxStatus(str, enum.Enum):
    LOCKED = "locked"


class TGUserCreditsTx(RecordModel):
    __tablename__ = "tg_user_credits_transactions"
    __table_args__ = (
        CheckConstraint(
            "amount > 0", name="tg_user_credits_transactions__amount_positive"
        ),
        Index("ix_tg_user_credits_transactions__deleted_at", "deleted_at"),
        Index(
            "ix_tg_user_credits_transactions__hanging_transactions",
            "created_at",
            "deleted_at",
            "status",
        ),
    )

    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[CreditsTxStatus] = mapped_column(
        Enum(
            CreditsTxStatus,
            name="tg_user_credits_transaction_status",
            values_callable=lambda e: [i.value for i in e],
        ),
        default=CreditsTxStatus.LOCKED,
        nullable=False,
    )
    # Foreign keys
    tg_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("tgbot_tg_users.tg_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
