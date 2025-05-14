from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from app.tgbot.auth.services import TGUserService


@asynccontextmanager
async def spend_credits(
    db_session: AsyncSession, tg_user_id: int, amount: int
) -> AsyncGenerator[None, None]:
    tg_user_svc = TGUserService(db_session)
    lock_tx_id = await tg_user_svc.lock_credits(tg_user_id, amount)
    try:
        yield
    except Exception:
        await tg_user_svc.unlock_credits(tg_user_id, lock_tx_id)
        raise
    await tg_user_svc.confirm_locked_credits(tg_user_id, lock_tx_id)
