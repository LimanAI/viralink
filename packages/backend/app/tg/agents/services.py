from typing import Any
from uuid import UUID

from sqlalchemy import sql

from app.services import BaseService

from .models import TGAgent, TGAgentStatus


class TGAgentService(BaseService):
    async def get(self, channel_id: int, tg_user_id: int) -> TGAgent | None:
        async with self.tx():
            result = await self.db_session.execute(
                sql.select(TGAgent).filter_by(channel_id=channel_id, user_id=tg_user_id)
            )
        return result.scalar_one_or_none()

    async def list(self, tg_user_id: int) -> list[TGAgent]:
        async with self.tx():
            result = await self.db_session.execute(
                sql.select(TGAgent)
                .filter_by(tg_user_id=tg_user_id, deleted_at=None)
                .order_by(TGAgent.created_at.asc())
            )
        return list(result.scalars().all())

    async def create(
        self,
        tg_user_id: int,
        channel_link: str,
    ) -> TGAgent:
        async with self.tx():
            result = await self.db_session.execute(
                sql.insert(TGAgent)
                .values(
                    channel_link=channel_link,
                    tg_user_id=tg_user_id,
                    status=TGAgentStatus.INITIAL,
                )
                .returning(TGAgent)
            )
        return result.scalar_one()
