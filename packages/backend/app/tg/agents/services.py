from typing import Any
from uuid import UUID

from sqlalchemy import sql
from sqlalchemy.orm import selectinload

from app.core.errors import ForbiddenError, NotFoundError
from app.models.base import ErrorSchema, utc_now
from app.services import BaseService
from app.tg.agents.models import BotMetadata, TGAgent, TGAgentStatus, TGUserBot


class TGAgentService(BaseService):
    async def get(self, agent_id: UUID, *, with_bot: bool = False) -> TGAgent | None:
        query = sql.select(TGAgent).filter_by(id=agent_id)
        if with_bot:
            query = query.options(selectinload(TGAgent.user_bot))
        async with self.tx():
            result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_for_channel(self, channel_id: int, tg_user_id: int) -> TGAgent | None:
        async with self.tx():
            result = await self.db_session.execute(
                sql.select(TGAgent).filter_by(channel_id=channel_id, user_id=tg_user_id)
            )
        return result.scalar_one_or_none()

    async def list_agents(self, tg_user_id: int) -> list[TGAgent]:
        async with self.tx():
            result = await self.db_session.execute(
                sql.select(TGAgent)
                .filter_by(tg_user_id=tg_user_id, deleted_at=None)
                .order_by(TGAgent.created_at.asc())
            )
        return list(result.scalars().all())

    async def list_bots(self, tg_user_id: int) -> list[TGUserBot]:
        async with self.tx():
            result = await self.db_session.execute(
                sql.select(TGUserBot)
                .filter_by(tg_user_id=tg_user_id)
                .order_by(TGUserBot.created_at.asc())
            )
        return list(result.scalars().all())

    async def create(
        self,
        tg_user_id: int,
        channel_username: str,
    ) -> TGAgent:
        async with self.tx():
            result = await self.db_session.execute(
                sql.insert(TGAgent)
                .values(
                    channel_username=channel_username.lstrip("@"),
                    tg_user_id=tg_user_id,
                    status=TGAgentStatus.WAITING_BOT_ATTACH,
                )
                .returning(TGAgent)
            )
        return result.scalar_one()

    async def create_and_link_bot(
        self, agent_id: UUID, tg_user_id: int, bot_token: str, bot_metadata: BotMetadata
    ) -> TGAgent:
        async with self.tx():
            agent = await self.get(agent_id)
            if not agent:
                raise ValueError("Agent not found")

            bot_result = await self.db_session.execute(
                sql.select(TGUserBot).filter_by(
                    tg_id=bot_metadata.id, tg_user_id=tg_user_id
                )
            )
            bot = bot_result.scalar_one_or_none()
            if bot is not None:
                raise ValueError("Bot already exists")

            bot = TGUserBot(
                tg_id=bot_metadata.id,
                api_token=bot_token,
                metadata_=bot_metadata,
                tg_user_id=tg_user_id,
            )
            self.db_session.add(bot)

            agent.user_bot = bot
            agent.status = TGAgentStatus.WAITING_BOT_ACCESS
        return agent

    async def link_bot(self, agent_id: UUID, tg_user_id: int, bot_id: UUID) -> TGAgent:
        async with self.tx():
            agent = await self.get(agent_id)
            if not agent:
                raise NotFoundError(
                    "Agent not found", tg_user_id=tg_user_id, agent_id=agent_id
                )

            bot_result = await self.db_session.execute(
                sql.select(TGUserBot).filter_by(id=bot_id, tg_user_id=tg_user_id)
            )
            bot = bot_result.scalar_one_or_none()
            if not bot:
                raise NotFoundError(
                    "Bot does not exist", tg_user_id=tg_user_id, bot_id=bot_id
                )

            if bot.tg_user_id != tg_user_id:
                raise ForbiddenError(
                    "Bot does not belong to user", tg_user_id=tg_user_id, bot_id=bot_id
                )

            agent.user_bot = bot
            agent.status = TGAgentStatus.WAITING_BOT_ACCESS
        return agent

    async def waiting_bot_attach(self, agent_id: UUID) -> TGAgent:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAgent)
                .filter_by(id=agent_id)
                .values(
                    status=TGAgentStatus.WAITING_BOT_ATTACH,
                    status_changed_at=utc_now(),
                    status_error=None,
                    status_errored_at=None,
                )
                .returning(TGAgent)
            )
        return result.scalar_one()

    async def waiting_bot_access(self, agent_id: UUID) -> TGAgent:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAgent)
                .filter_by(id=agent_id)
                .values(
                    status=TGAgentStatus.WAITING_BOT_ACCESS,
                    status_changed_at=utc_now(),
                    status_error=None,
                    status_errored_at=None,
                )
                .returning(TGAgent)
            )
        return result.scalar_one()

    async def save_status_error(self, agent_id: UUID, status_error: str) -> TGAgent:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAgent)
                .filter_by(id=agent_id)
                .values(
                    status_error=ErrorSchema(message=status_error),
                    status_errored_at=utc_now(),
                )
                .returning(TGAgent)
            )
        return result.scalar_one()
