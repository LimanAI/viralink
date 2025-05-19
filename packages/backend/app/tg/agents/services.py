from typing import Any, Literal, overload
from uuid import UUID

from sqlalchemy import sql
from sqlalchemy.orm import selectinload
from telegram import ChatFullInfo

from app.core.errors import AppError, ForbiddenError, NotFoundError
from app.models.base import ErrorSchema, utc_now
from app.services import BaseService
from app.tg.agents.models import (
    BotMetadata,
    BotPermissions,
    ChannelMetadata,
    ChannelProfile,
    TGAgent,
    TGAgentJob,
    TGAgentJobStatus,
    TGAgentJobType,
    TGAgentStatus,
    TGUserBot,
)


class TGAgentService(BaseService):
    @overload
    async def get(
        self, agent_id: UUID, *, required: Literal[True], with_bot: bool = False
    ) -> TGAgent: ...
    @overload
    async def get(
        self,
        agent_id: UUID,
        *,
        required: Literal[False] = False,
        with_bot: bool = False,
    ) -> TGAgent | None: ...

    async def get(
        self, agent_id: UUID, *, required: bool = False, with_bot: bool = False
    ) -> TGAgent | None:
        query = sql.select(TGAgent).filter_by(id=agent_id, deleted_at=None)
        if with_bot:
            query = query.options(selectinload(TGAgent.user_bot))
        async with self.tx():
            result = await self.db_session.execute(query)

        agent = result.scalar_one_or_none()
        if not agent and required:
            raise NotFoundError("Agent not found", agent_id=agent_id)
        return agent

    async def get_for_channel(self, channel_id: int, tg_user_id: int) -> TGAgent | None:
        async with self.tx():
            result = await self.db_session.execute(
                sql.select(TGAgent).filter_by(
                    channel_id=channel_id, user_id=tg_user_id, deleted_at=None
                )
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

    async def delete(self, agent_id: UUID, tg_user_id: int) -> TGAgent:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAgent)
                .filter_by(id=agent_id, tg_user_id=tg_user_id)
                .values(deleted_at=utc_now())
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

    async def waiting_channel_profile(self, agent_id: UUID) -> TGAgent:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAgent)
                .filter_by(id=agent_id)
                .values(
                    status=TGAgentStatus.WAITING_CHANNEL_PROFILE,
                    status_changed_at=utc_now(),
                    status_error=None,
                    status_errored_at=None,
                )
                .returning(TGAgent)
            )
        return result.scalar_one()

    async def activate(self, agent_id: UUID) -> TGAgent:
        async with self.tx():
            agent = await self.get(agent_id)

            if not agent:
                raise NotFoundError("Agent not found", agent_id=agent_id)

            if agent.status not in [
                TGAgentStatus.WAITING_BOT_ACCESS,
                TGAgentStatus.WAITING_CHANNEL_PROFILE,
                TGAgentStatus.DISABLED,
                TGAgentStatus.DISABLED_NO_CREDIT,
            ]:
                raise AppError(
                    "Agent is not in a state to be activated",
                    agent_id=agent_id,
                    status=agent.status,
                )

            agent.status = TGAgentStatus.ACTIVE
            agent.status_changed_at = utc_now()
            agent.status_error = None
            agent.status_errored_at = None
        return agent

    async def update_bot_permissions(
        self, agent_id: UUID, bot_id: UUID, bot_permissions: BotPermissions
    ) -> TGAgent:
        async with self.tx():
            agent = await self.get(agent_id, with_bot=True)
            if not agent:
                raise NotFoundError("Agent not found", agent_id=agent_id)

            if agent.user_bot.id != bot_id:
                raise ForbiddenError(
                    "Bot ID does not match the agent's bot ID",
                    agent_id=agent_id,
                    bot_id=bot_id,
                )

            agent.bot_permissions = bot_permissions
        return agent

    async def update_channel_metadata(
        self,
        agent_id: UUID,
        channel_metadata: ChannelMetadata,
    ) -> TGAgent:
        async with self.tx():
            agent = await self.get(agent_id)
            if not agent:
                raise NotFoundError("Agent not found", agent_id=agent_id)

            if agent.channel_username != channel_metadata.username:
                raise ValueError(
                    "Channel username does not match the agent's channel username"
                )

            result = await self.db_session.execute(
                sql.update(TGAgent)
                .filter_by(id=agent_id)
                .values(
                    channel_id=channel_metadata.id,
                    channel_metadata=channel_metadata,
                )
                .returning(TGAgent)
            )
            agent = result.scalar_one()
        return agent

    async def update_channel_profile(
        self,
        agent_id: UUID,
        content_description: str | None = None,
        persona_description: str | None = None,
    ) -> TGAgent:
        if content_description is None and persona_description is None:
            raise ValueError(
                "At least one of content_description or persona_description must be provided"
            )
        async with self.tx():
            agent = await self.get(agent_id)
            if not agent:
                raise NotFoundError("Agent not found", agent_id=agent_id)

            # TODO: supports incremental json updates
            agent.channel_profile = ChannelProfile(
                content_description=content_description
                or agent.channel_profile.content_description,
                persona_description=persona_description
                or agent.channel_profile.persona_description,
            )
        return agent

    async def update_channel_profile_generated(
        self,
        agent_id: UUID,
        channel_profile_generated: str,
    ) -> TGAgent:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAgent)
                .filter_by(id=agent_id)
                .values(channel_profile_generated=channel_profile_generated)
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


class TGAgentJobService(BaseService):
    async def create(
        self,
        agent_id: UUID,
        metadata: dict[Any, Any],
        type_: Literal[TGAgentJobType.POST_GENERATION, TGAgentJobType.POST_UPDATE],
    ) -> TGAgentJob:
        async with self.tx():
            result = await self.db_session.execute(
                sql.insert(TGAgentJob)
                .values(
                    agent_id=agent_id,
                    metadata_=metadata,
                    status=TGAgentJobStatus.INITIAL,
                    type_=type_,
                )
                .returning(TGAgentJob)
            )
        return result.scalar_one()

    @overload
    async def get(
        self,
        job_id: UUID,
        *,
        required: Literal[True],
        type_: TGAgentJobType | None = None,
    ) -> TGAgentJob: ...
    @overload
    async def get(
        self,
        job_id: UUID,
        *,
        required: Literal[False] = False,
        type_: TGAgentJobType | None = None,
    ) -> TGAgentJob | None: ...

    async def get(
        self,
        job_id: UUID,
        *,
        required: bool = False,
        type_: TGAgentJobType | None = None,
    ) -> TGAgentJob | None:
        query = sql.select(TGAgentJob).filter_by(id=job_id, deleted_at=None)
        async with self.tx():
            result = await self.db_session.execute(query)
        job = result.scalar_one_or_none()

        if not job:
            if required:
                raise NotFoundError("Agent job not found", job_id=job_id)
            return None

        if type_ and job.type_ != type_:
            raise AppError(
                f"Agent job type mismatch, expected_type: {type_}, actual_type: {job.type_}",
                job_id=job_id,
            )
        return job

    async def in_progress(self, job_id: UUID) -> TGAgentJob:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAgentJob)
                .filter_by(id=job_id, status=TGAgentJobStatus.INITIAL, deleted_at=None)
                .values(
                    status=TGAgentJobStatus.IN_PROGRESS,
                    status_changed_at=utc_now(),
                    status_error=None,
                    status_errored_at=None,
                )
                .returning(TGAgentJob)
            )
        return result.scalar_one()

    async def complete(self, job_id: UUID, data: str) -> TGAgentJob:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAgentJob)
                .filter_by(
                    id=job_id, status=TGAgentJobStatus.IN_PROGRESS, deleted_at=None
                )
                .values(
                    status=TGAgentJobStatus.COMPLETED,
                    status_changed_at=utc_now(),
                    status_error=None,
                    status_errored_at=None,
                    data=data,
                )
                .returning(TGAgentJob)
            )
        return result.scalar_one()
