from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from arq.connections import create_pool
from telegram import BotCommand, Update

from app.db import AsyncSessionMaker
from app.tgbot.app import TGApp, tg_app
from app.tgbot.context import Context
from app.tgbot.handlers import handlers
from app.worker.conf import WorkerSettings

logger = structlog.get_logger()


async def error_handler(_: object, context: Context) -> None:
    logger.exception("Exception while handling update:", exc_info=context.error)


@asynccontextmanager
async def start_tg_app(session_maker: AsyncSessionMaker) -> AsyncGenerator[TGApp, None]:
    tg_app.add_handlers(handlers)
    tg_app.add_error_handler(error_handler)
    Context.db_session_maker = session_maker
    Context.arq = await create_pool(
        WorkerSettings.redis_settings, default_queue_name=WorkerSettings.queue_name
    )

    async with tg_app:
        if tg_app.post_init is not None:
            await tg_app.post_init(tg_app)

        if tg_app.updater is not None:
            await tg_app.updater.start_polling()
            logger.info("Telegram bot polling started")

        await tg_app.start()
        logger.info("Telegram bot started")

        yield tg_app

        await Context.arq.aclose()
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
        "add_channel": "Add channel",
    }
    # localize
    for lang in ["en", "ru"]:
        await tg_app.bot.set_my_commands(
            [BotCommand(k, v) for k, v in commands.items()],
            language_code=lang,
        )
