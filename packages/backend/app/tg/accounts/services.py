from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from telethon import TelegramClient
from telethon.sessions import StringSession

from app.tg.accounts.models import TGAccountModel, TGAccountStatus

from .repositories import TGAccountRepository

logger = structlog.get_logger()


class TGAccountService(TGAccountRepository):
    def __init__(
        self,
        db_session: AsyncSession,
    ) -> None:
        super().__init__(db_session=db_session)
        self.tg_agent_repo = TGAccountRepository(db_session=db_session)

    @asynccontextmanager
    async def get_tgclient(
        self, tg_account: TGAccountModel
    ) -> AsyncGenerator[TelegramClient, None]:
        session_string = StringSession(tg_account.session_string)
        try:
            async with TelegramClient(
                session_string, tg_account.api_id, tg_account.api_hash
            ) as tgclient:
                yield tgclient
        except Exception as e:
            logger.exception(
                f"Error in TelegramClient context manager for account {tg_account.id}: {e}"
            )
            raise e
            # TODO: Handle session expiration and re-login

    async def get_available(self) -> TGAccountModel:
        tg_accounts = await self.tg_agent_repo.list(status=TGAccountStatus.ACTIVE)
        for tg_account in tg_accounts:
            async with self.get_tgclient(tg_account) as tgclient:
                if await tgclient.is_user_authorized():
                    return tg_account
        raise Exception("All tg_accounts are not available")
