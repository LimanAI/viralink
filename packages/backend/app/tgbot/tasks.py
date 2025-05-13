import asyncio
import io
from uuid import UUID

import structlog
from telegram import Bot

from app.conf import settings
from app.core.errors import AppError, NotFoundError
from app.core.utils import get_s3_client
from app.tg.agents.models import ChannelMetadata
from app.tg.agents.services import TGAgentService
from app.worker.conf import JobContext, task

logger = structlog.get_logger()


@task("fetch_channel_photo")
async def fetch_channel_photo(ctx: JobContext, agent_id: UUID) -> None:
    tg_agent_svc = TGAgentService(ctx.db_session)
    agent = await tg_agent_svc.get(agent_id, with_bot=True)
    if not agent:
        raise NotFoundError("Agent not found", agent_id=agent_id)

    if not agent.channel_metadata:
        raise NotFoundError("Channel metadata not found", agent_id=agent_id)

    if not agent.user_bot:
        raise NotFoundError("User bot not found", agent_id=agent_id)

    if not agent.tg_user_id:
        raise AppError("Agent is detached from user", agent_id=agent_id)

    if not agent.channel_metadata.photo:
        raise NotFoundError("Channel photo not found", agent_id=agent_id)

    bot = Bot(agent.user_bot.api_token)
    channel_metadata = ChannelMetadata(**agent.channel_metadata.model_dump())
    photo = channel_metadata.photo
    if not photo:
        raise NotFoundError("Channel photo not found", agent_id=agent_id)

    if photo.small_file_id:
        file_path = await _upload_file_id(bot, agent.tg_user_id, photo.small_file_id)
        photo.small_file_path = file_path

    if photo.big_file_id:
        file_path = await _upload_file_id(bot, agent.tg_user_id, photo.big_file_id)
        photo.big_file_path = file_path

    agent = await tg_agent_svc.update_channel_metadata(agent_id, channel_metadata)


async def _upload_file_id(bot: Bot, tg_user_id: int, file_id: str) -> str:
    file_path = f"{tg_user_id}/bot/{file_id}"
    s3_client = get_s3_client()

    file = await bot.get_file(file_id)
    buffer = io.BytesIO()
    await file.download_to_memory(buffer)
    buffer.seek(0)

    def upload(buffer: io.BytesIO) -> None:
        s3_client.upload_fileobj(buffer, settings.STORAGE_BUCKET, file_path)

    await asyncio.get_event_loop().run_in_executor(None, upload, buffer)
    logger.info(f"File uploaded {file_path}")

    return file_path
