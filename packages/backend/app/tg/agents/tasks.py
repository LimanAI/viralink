import tempfile
import urllib.request
from uuid import UUID

import structlog
from telegram import Bot
from telegram.constants import ParseMode

from app.conf import settings
from app.core.errors import AppError, NotFoundError
from app.tg.agents.models import TGAgentJobStatus, TGAgentJobType
from app.tg.agents.post_generator.post_generator import (
    PostGenerator,
    check_if_job_staled,
)
from app.tg.agents.services import TGAgentJobService, TGAgentService
from app.tgbot.auth.services import TGUserService
from app.worker.conf import JobContext, task

logger = structlog.get_logger()


@task("generate_post")
async def generate_post(ctx: JobContext, job_id: UUID, from_chat_id: int) -> None:
    agent_svc = TGAgentService(ctx.db_session)
    agent_job_svc = TGAgentJobService(ctx.db_session)

    job = await agent_job_svc.get(job_id)
    if not job:
        raise NotFoundError("Job not found", job_id=job_id)

    if job.type_ != TGAgentJobType.POST_GENERATION:
        raise AppError(
            f"Job is not a root job with POST_GENERATION type, actual {job.type_}",
            job_id=job_id,
        )

    check_if_job_staled(job)
    if job.status != TGAgentJobStatus.INITIAL:
        raise AppError(
            "Job is not in INITIAL status, acutal {job.status}", job_id=job_id
        )

    if not job.agent_id:
        raise AppError("Job is detached from agent", job_id=job_id)

    agent = await agent_svc.get(job.agent_id, with_bot=True)
    if not agent:
        raise AppError("Agent not found", job_id=job_id, agent_id=job.agent_id)
    if not agent.tg_user_id:
        raise AppError("Agent is orphaned", job_id=job_id, agent_id=job.agent_id)

    post_generator = PostGenerator(ctx.db_session_maker, ctx.db_session)
    post_text = await post_generator.generate(job)

    await agent_job_svc.complete(job.id, post_text)

    await Bot(settings.TGBOT_TOKEN.get_secret_value()).send_message(
        from_chat_id, post_text, parse_mode=ParseMode.HTML
    )


@task("update_post")
async def update_post(ctx: JobContext, job_id: UUID, from_chat_id: int) -> None:
    agent_svc = TGAgentService(ctx.db_session)
    agent_job_svc = TGAgentJobService(ctx.db_session)

    job = await agent_job_svc.get(job_id)
    if not job:
        raise AppError("Job not found", job_id=job_id)

    if job.type_ != TGAgentJobType.POST_UPDATE:
        raise AppError(
            f"Job is not a root job with POST_UPDATE type, actual {job.type_}",
            job_id=job_id,
        )

    check_if_job_staled(job)
    if job.status != TGAgentJobStatus.INITIAL:
        raise AppError(
            "Job is not in INITIAL status, acutal {job.status}", job_id=job_id
        )

    if not job.agent_id:
        raise AppError("Job is detached from agent", job_id=job_id)

    agent = await agent_svc.get(job.agent_id, with_bot=True)
    if not agent:
        raise AppError("Agent not found", job_id=job_id, agent_id=job.agent_id)

    post_generator = PostGenerator(ctx.db_session_maker, ctx.db_session)
    data = None
    try:
        data = await post_generator.update(job)
    except AppError as e:
        if e.code == 2200:
            await Bot(settings.TGBOT_TOKEN.get_secret_value()).send_message(
                from_chat_id,
                text="Сообщение слишком длинное для герерации изображения, сначала сделайте его короче.",
            )
            return
        logger.exception(f"AppError: {e}")
        raise
    except Exception as e:
        logger.exception(e)
    finally:
        post_text = data.get("message", "") if data else ""
        await agent_job_svc.complete(job.id, "")

    image = data and data.get("image")
    image_path: str | None = None
    if image:
        image_path = await download_image(image)
    try:
        if from_chat_id and post_text:
            if image_path:
                await Bot(settings.TGBOT_TOKEN.get_secret_value()).send_photo(
                    from_chat_id,
                    photo=image_path,
                    caption=post_text,
                    parse_mode=ParseMode.HTML,
                )
            else:
                await Bot(settings.TGBOT_TOKEN.get_secret_value()).send_message(
                    from_chat_id, post_text, parse_mode=ParseMode.HTML
                )
    except Exception as e:
        logger.exception(e)


async def download_image(url: str) -> str:
    # Create temp file in /tmp with .jpg suffix
    with tempfile.NamedTemporaryFile(delete=False, dir="/tmp") as tmp_file:
        tmp_path = tmp_file.name
        # Download image from URL and write it to the temp file
        with urllib.request.urlopen(url) as response:
            tmp_file.write(response.read())
    return tmp_path
