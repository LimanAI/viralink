from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from telegram import BotCommand

from app.db import AsyncSessionMaker
from app.tgbot.app import TGApp, tg_app
from app.tgbot.context import Context
from app.tgbot.handlers import handlers

logger = structlog.get_logger()


@asynccontextmanager
async def start_tg_app(session_maker: AsyncSessionMaker) -> AsyncGenerator[TGApp, None]:
    tg_app.add_handlers(handlers)
    Context.db_session_maker = session_maker

    async with tg_app:
        if tg_app.post_init is not None:
            await tg_app.post_init(tg_app)

        if tg_app.updater is not None:
            await tg_app.updater.start_polling()
            logger.info("Telegram bot polling started")

        await tg_app.start()
        logger.info("Telegram bot started")

        yield tg_app

        if tg_app.updater is not None:
            await tg_app.updater.stop()
        await tg_app.stop()
        if tg_app.post_stop is not None:
            await tg_app.post_stop(tg_app)
    if tg_app.post_shutdown is not None:
        await tg_app.post_shutdown(tg_app)


async def setup_commands(tg_app: TGApp) -> None:
    commands = {
        "start": "start",
    }
    # localize
    for lang in ["en", "ru"]:
        await tg_app.bot.set_my_commands(
            [BotCommand(k, v) for k, v in commands.items()],
            language_code=lang,
        )
