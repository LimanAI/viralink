from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from telegram.ext import CallbackContext, ExtBot

from app.db import AsyncSessionMaker
from app.tgbot.auth.models import TGUser


class Context(
    CallbackContext[ExtBot[None], dict[Any, Any], dict[Any, Any], dict[Any, Any]]
):
    db_session: AsyncSession | None = None
    db_session_maker: AsyncSessionMaker

    tg_user: TGUser | None = None
