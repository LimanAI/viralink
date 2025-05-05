from uuid import UUID

from sqlalchemy import sql

from app.models.base import ErrorSchema
from app.services import BaseRepository
from app.tg.accounts.models import TGAccountModel, TGAccountStatus
from app.tg.accounts.schemas import CreateAccountRequest


class TGAccountRepository(BaseRepository):
    async def create_account(
        self,
        payload: CreateAccountRequest,
    ) -> TGAccountModel:
        async with self.tx():
            result = await self.db_session.execute(
                sql.insert(TGAccountModel)
                .values(**payload.model_dump(), status=TGAccountStatus.INITIAL)
                .returning(TGAccountModel)
            )
        return result.scalar_one()

    async def get_account(self, account_id: UUID) -> TGAccountModel | None:
        async with self.tx():
            result = await self.db_session.execute(
                sql.select(TGAccountModel).filter_by(id=account_id)
            )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        exclude_ids: list[UUID] | None = None,
        status: TGAccountStatus | None = None,
    ) -> list[TGAccountModel]:
        query = sql.select(TGAccountModel)
        if exclude_ids:
            query = query.where(TGAccountModel.id.notin_(exclude_ids))
        if status:
            query = query.filter_by(status=status)
        async with self.tx():
            result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def update_phone_number(
        self,
        account_id: UUID,
        phone_number: str,
        phone_code_hash: str,
    ) -> TGAccountModel:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAccountModel)
                .filter_by(id=account_id)
                .values(phone_number=phone_number, phone_code_hash=phone_code_hash)
                .returning(TGAccountModel)
            )
        return result.scalar_one()

    async def update_status(
        self, account_id: UUID, status: TGAccountStatus
    ) -> TGAccountModel:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAccountModel)
                .filter_by(id=account_id)
                .values(
                    status=status,
                    status_changed_at=sql.func.now(),
                    status_error=None,
                    status_errored_at=None,
                )
                .returning(TGAccountModel)
            )
        return result.scalar_one()

    async def save_status_error(
        self,
        account_id: UUID,
        status_error: ErrorSchema,
    ) -> TGAccountModel:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAccountModel)
                .filter_by(id=account_id)
                .values(
                    status_error=status_error,
                    status_errored_at=sql.func.now(),
                )
                .returning(TGAccountModel)
            )
        return result.scalar_one()

    async def save_session_string(
        self, account_id: UUID, session_string: str
    ) -> TGAccountModel:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAccountModel)
                .filter_by(id=account_id)
                .values(session_string=session_string)
                .returning(TGAccountModel)
            )
        return result.scalar_one()

    async def get_account_with_least_watched_channels(self) -> TGAccountModel:
        async with self.tx():
            result = await self.db_session.execute(
                sql.select(TGAccountModel)
                .order_by(TGAccountModel.watched_channels_count)
                .limit(1)
            )
        return result.scalar_one()
