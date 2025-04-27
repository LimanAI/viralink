from sqlalchemy import sql

from app.services import BaseService
from app.tgbot.auth.models import TGUserModel
from app.tgbot.schemas import UserTGData


class TGUserService(BaseService):
    async def get_user_and_update(
        self,
        user_data: UserTGData,
    ) -> TGUserModel:
        async with self.tx():
            result = await self.db_session.execute(
                sql.select(TGUserModel).filter_by(id=user_data.tg_id)
            )
            tg_user = result.scalar_one_or_none()

            # signup
            if not tg_user:
                tg_user = TGUserModel(**user_data.model_dump())
                self.db_session.add(tg_user)
            # update
            elif diff := tg_user.get_diff(user_data):
                result = await self.db_session.execute(
                    sql.update(TGUserModel)
                    .filter_by(id=user_data.tg_id)
                    .values(**diff)
                    .returning(TGUserModel)
                )
                tg_user = result.scalar_one()

        return tg_user
