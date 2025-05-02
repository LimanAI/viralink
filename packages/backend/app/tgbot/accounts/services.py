from sqlalchemy import sql

from app.services import BaseService
from app.tgbot.accounts.models import TGAccountModel, TGAccountStatus
from app.tgbot.accounts.schemas import CreateAccountRequest


class TGAccountService(BaseService):
    async def create_account(
        self,
        payload: CreateAccountRequest,
    ) -> TGAccountModel:
        async with self.tx():
            result = await self.db_session.execute(
                sql.insert(TGAccountModel)
                .values(**payload.model_dump())
                .returning(TGAccountModel)
            )
        return result.scalar_one()

    async def get_account(self, api_id: int) -> TGAccountModel | None:
        async with self.tx():
            result = await self.db_session.execute(
                sql.select(TGAccountModel).filter_by(api_id=api_id)
            )
        return result.scalar_one_or_none()

    async def update_phone_number(
        self, tg_account_model: TGAccountModel, phone_number: str
    ) -> TGAccountModel:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAccountModel)
                .filter_by(id=tg_account_model.id)
                .values(phone_number=phone_number)
                .returning(TGAccountModel)
            )
        return result.scalar_one()

    async def update_status(
        self, tg_account_model: TGAccountModel, status: TGAccountStatus
    ) -> TGAccountModel:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAccountModel)
                .filter_by(id=tg_account_model.id)
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
        tg_account_model: TGAccountModel,
        status_error: dict[str, str],
    ) -> TGAccountModel:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAccountModel)
                .filter_by(id=tg_account_model.id)
                .values(
                    status_error=status_error,
                    status_errored_at=sql.func.now(),
                )
                .returning(TGAccountModel)
            )
        return result.scalar_one()

    async def save_session_string(
        self, tg_account_model: TGAccountModel, session_string: str
    ) -> TGAccountModel:
        async with self.tx():
            result = await self.db_session.execute(
                sql.update(TGAccountModel)
                .filter_by(id=tg_account_model.id)
                .values(session_string_string=session_string)
                .returning(TGAccountModel)
            )
        return result.scalar_one()
