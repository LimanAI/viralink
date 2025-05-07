from sqlalchemy import sql

from app.services import BaseService
from app.tgbot.auth.models import TGUser
from app.tgbot.schemas import UserTGData


class TGUserService(BaseService):
    async def create(self, user_data: UserTGData) -> TGUser:
        async with self.tx():
            result = await self.db_session.execute(
                sql.insert(TGUser).values(**user_data.model_dump()).returning(TGUser)
            )
        return result.scalar_one()

    async def get_user_and_update(
        self,
        user_data: UserTGData,
    ) -> TGUser | None:
        async with self.tx():
            result = await self.db_session.execute(
                sql.select(TGUser).filter_by(tg_id=user_data.tg_id)
            )
            tg_user = result.scalar_one_or_none()

            if not tg_user:
                return None

            # update
            if diff := tg_user.get_diff(user_data):
                result = await self.db_session.execute(
                    sql.update(TGUser)
                    .filter_by(tg_id=user_data.tg_id)
                    .values(**diff)
                    .returning(TGUser)
                )
                tg_user = result.scalar_one()

        return tg_user
