from typing import Any
from uuid import UUID

from sqlalchemy import sql

from app.models.base import ErrorSchema, utc_now
from app.services import BaseRepository

from .models import TGAgent, TGChannel, TGChannelConnection, TGChannelConnectionStatus


class TGAgentRepository(BaseRepository):
    async def get_for_channel(
        self, tg_channel_id: int, tg_user_id: int | None, user_id: UUID | None
    ) -> TGAgent | None:
        if tg_user_id is not None and user_id is not None:
            raise ValueError("Only one of tg_user_id or user_id must be provided")

        query = sql.select(TGAgent).filter_by(tg_channel_id=tg_channel_id)
        if tg_user_id is not None:
            query = query.filter_by(tg_user_id=tg_user_id)
        elif user_id is not None:
            query = query.filter_by(user_id=user_id)
        else:
            raise ValueError("Either tg_user_id or user_id must be provided")

        async with self.tx():
            result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def create(
        self,
        tg_channel_id: int,
        tg_account_id: UUID,
        tg_user_id: int | None,
        user_id: UUID | None,
    ) -> TGAgent:
        if tg_user_id is not None and user_id is not None:
            raise ValueError("Only one of tg_user_id or user_id must be provided")

        kwargs: dict[str, Any] = {}
        if tg_user_id is not None:
            kwargs["tg_user_id"] = tg_user_id
        elif user_id is not None:
            kwargs["user_id"] = user_id
        else:
            raise ValueError("Either tg_user_id or user_id must be provided")

        async with self.tx():
            result = await self.db_session.execute(
                sql.insert(TGAgent)
                .values(
                    tg_channel_id=tg_channel_id, tg_account_id=tg_account_id, **kwargs
                )
                .returning(TGAgent)
            )
        return result.scalar_one()


class TGChannelRepository(BaseRepository):
    async def get_or_create(self, channel_id: int) -> TGChannel:
        async with self.tx():
            result = await self.db_session.execute(
                sql.select(TGChannel).filter_by(tg_channel_id=channel_id)
            )
            existing = result.scalar_one_or_none()
            if existing:
                return existing

            result = await self.db_session.execute(
                sql.insert(TGChannel)
                .values(tg_channel_id=channel_id)
                .returning(TGChannel)
            )
        return result.scalar_one()


class TGChannelConnectionRepository(BaseRepository):
    async def create(
        self, tg_account_id: UUID, tg_channel_id: int, access_hash: int
    ) -> TGChannelConnection:
        async with self.tx():
            result = await self.db_session.execute(
                sql.insert(TGChannelConnection)
                .values(
                    tg_channel_id=tg_channel_id,
                    tg_account_id=tg_account_id,
                    access_hash=access_hash,
                )
                .returning(TGChannelConnection)
            )
        return result.scalar_one()

    async def list(self, tg_channel_id: int) -> list[TGChannelConnection]:
        async with self.tx():
            result = await self.db_session.execute(
                sql.select(TGChannelConnection).filter_by(tg_channel_id=tg_channel_id)
            )
        return list(result.scalars().all())

    async def update_status(
        self,
        connection_id: int,
        status: TGChannelConnectionStatus,
        *,
        error: str | None = None,
        access_hash: int | None = None,
    ) -> TGChannelConnection:
        kwargs: dict[str, Any] = {
            "status_error": ErrorSchema(message=error) if error else None,
            "status_errored_at": utc_now() if error else None,
        }
        if access_hash is not None:
            kwargs["access_hash"] = access_hash
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGChannelConnection)
                .filter_by(
                    id=connection_id,
                )
                .values(status=status, status_updated_at=utc_now(), **kwargs)
                .returning(TGChannelConnection)
            )
        return result.scalar_one()
