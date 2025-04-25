from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import structlog
from telegram import BotCommand
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ContextTypes,
    ExtBot,
)

from app.conf import settings
from app.tgbot.context import Context
from app.tgbot.handlers import handlers

logger = structlog.get_logger()

TGApp = Application[
    ExtBot[None], Context, dict[Any, Any], dict[Any, Any], dict[Any, Any], None
]


@asynccontextmanager
async def start_tg_app() -> AsyncGenerator[TGApp, None]:
    builder = (
        ApplicationBuilder()
        .context_types(ContextTypes(context=Context))
        .job_queue(None)
        .token(settings.TGBOT_TOKEN.get_secret_value())
    )

    tg_app = (
        builder.build() if settings.TGBOT_POOLING else builder.updater(None).build()
    )

    tg_app.add_handlers(handlers)

    async with tg_app:
        await tg_app.start()
        logger.info("Telegram bot started")

        if tg_app.updater is not None:
            await tg_app.updater.start_polling()
            logger.info("Telegram bot polling started")

        yield tg_app

        if tg_app.updater is not None:
            await tg_app.updater.stop()
        await tg_app.stop()


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
