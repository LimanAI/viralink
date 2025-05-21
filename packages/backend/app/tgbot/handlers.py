import asyncio
import io
from pathlib import Path
from uuid import UUID

import structlog
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, filters
from telethon.errors import re

from app.conf import settings
from app.core.errors import AppError
from app.core.llm import get_llm, load_prompts
from app.db import AsyncSessionMaker
from app.tg.agents.models import (
    PostUpdateMetadata,
    TGAgentJobStatus,
    TGAgentJobType,
    TGAgentStatus,
)
from app.tg.agents.services import TGAgentJobService, TGAgentService
from app.tgbot.auth.errors import InvalidInviteCodeError
from app.tgbot.auth.services import TGInviteCodesService, TGUserService
from app.tgbot.context import Context
from app.tgbot.decorators import db_session, requires_auth
from app.tgbot.utils import (
    LocalizedTexts,
    extract_user_data,
    get_invite_code,
    get_texts,
)

logger = structlog.get_logger()


class StartTexts(BaseModel):
    welcome_text: str
    welcome_back_text: str


class HandlersTexts(BaseModel):
    start: StartTexts


class Texts(LocalizedTexts[HandlersTexts]):
    en: HandlersTexts
    ru: HandlersTexts


class GenerateChannelProfilePrompts(BaseModel):
    system_prompt: str
    channel_profile_generated: str
    post_message: str


class LangPrompts(BaseModel):
    generate_channel_profile: GenerateChannelProfilePrompts


class Prompts(BaseModel):
    ru: LangPrompts


try:
    TEXTS = load_prompts(
        Path(__file__).parent / "texts.yaml",
        Texts,
        key="handlers",
    )
    PROMPTS = load_prompts(
        Path(__file__).parent / "texts.yaml",
        Prompts,
        key="prompts",
    )
except:
    logger.error("Failed to load PostGenerator prompts")
    raise


@db_session
async def start(update: Update, context: Context) -> None:
    user_data = extract_user_data(update)
    if user_data is None:
        raise ValueError("User data is None")
    # TODO: provide in context
    if not context.db_session:
        raise ValueError("DB session is None")

    texts = get_texts(TEXTS, user_data.language_code)
    chat = update.effective_chat
    if not chat:
        return

    user_svc = TGUserService(context.db_session)
    user = await user_svc.get_user_and_update(user_data)
    if not user:
        invite_code = get_invite_code(context)
        try:
            user = await user_svc.create(user_data, invite_code=invite_code)
        except InvalidInviteCodeError as e:
            logger.exception(e)
            await chat.send_message(
                text=texts.start.welcome_text,
            )
            return
    await chat.send_message(
        text=texts.start.welcome_back_text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Setup", web_app=WebAppInfo(settings.WEBAPP_URL))]]
        ),
    )


@db_session
@requires_auth
async def process_request(update: Update, context: Context) -> None:
    user_data = extract_user_data(update)
    if user_data is None:
        raise ValueError("User data is None")

    logger.info(f"Processing request for {user_data.tg_id}", tg_user_id=user_data.tg_id)
    db_session = context.db_session
    if not db_session:
        raise ValueError("Database session is None")
    tg_user_svc = TGUserService(db_session)
    user = await tg_user_svc.get_user_and_update(user_data)

    message = update.message
    if not message:
        raise ValueError("update.message is None")
    if not user:
        await message.reply_text(
            text="Please setup your profile.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Setup", web_app=WebAppInfo(settings.WEBAPP_URL)
                        )
                    ]
                ]
            ),
        )
        return

    agent_svc = TGAgentService(db_session)
    agents = await agent_svc.list_agents(user.tg_id)
    active_agents = [agent for agent in agents if agent.status == TGAgentStatus.ACTIVE]

    if not active_agents:
        await message.reply_text(
            text="You have no active agents. Please add a channel.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Add Channel", web_app=WebAppInfo(settings.WEBAPP_URL)
                        )
                    ]
                ]
            ),
        )
        return

    # TODO: generate for the first active agent
    agent = await agent_svc.get(active_agents[0].id, with_bot=True)
    if not agent:
        raise AppError(f"There is no needful agent {agents[0]}")
    if not agent.tg_user_id:
        raise AppError("Agent is detached from user", agent_id=agent.id)

    agent_job_svc = TGAgentJobService(db_session)
    message_text = message.text
    if not message_text:
        raise AppError("Message text is None")

    logger.debug(message_text)
    if not update.effective_chat:
        raise ValueError("context.effective_chat is None")

    if message.reply_to_message:
        notify_message = await message.reply_text(text="Updating the post...")
        replied_message = (
            message.reply_to_message.text or message.reply_to_message.caption
        )
        photos = message.reply_to_message.photo
        job = await agent_job_svc.create(
            tg_user_id=agent.tg_user_id,
            agent_id=agent.id,
            metadata={
                "user_prompt": message_text,
                "original_message": replied_message,
                "notify_message_id": notify_message.message_id,
                "chat_id": update.effective_chat.id,
                "photo_id": photos[-1].file_id if photos else None,
            },
            type_=TGAgentJobType.POST_UPDATE,
        )
        await context.arq.enqueue_job("update_post", job.id, update.effective_chat.id)
    else:
        notify_message = await message.reply_text(text="Generating post...")
        job = await agent_job_svc.create(
            tg_user_id=agent.tg_user_id,
            agent_id=agent.id,
            metadata={
                "user_prompt": message_text,
                "notify_message_id": notify_message.message_id,
                "chat_id": update.effective_chat.id,
            },
            type_=TGAgentJobType.POST_GENERATION,
        )
        await context.arq.enqueue_job("generate_post", job.id, update.effective_chat.id)


@db_session
@requires_auth
async def publish_post(update: Update, context: Context) -> None:
    # TODO: provide in context
    if not context.db_session:
        raise ValueError("DB session is None")
    if not context.tg_user:
        raise ValueError("TG user is None")

    reg = rf"^/publish-post/({UUID_PATTERN})"
    callback_query = update.callback_query
    if not callback_query:
        raise ValueError("update.callback_query is None")
    match = re.match(reg, callback_query.data or "")
    if not match:
        raise ValueError("Callback query data is None")
    job_id = UUID(match.group(1))

    agent_job_svc = TGAgentJobService(context.db_session)
    job = await agent_job_svc.get(job_id)
    if not job:
        raise AppError("Job not found", job_id=job_id)

    if not job.tg_user_id != context.tg_user.tg_id:
        raise AppError(
            "Job is not created by the user",
            job_id=job_id,
            tg_user_id=context.tg_user.tg_id,
        )

    if job.type_ != TGAgentJobType.POST_UPDATE:
        raise AppError(
            f"Job is not a root job with POST_UPDATE type, actual {job.type_}",
            job_id=job_id,
        )

    if job.status != TGAgentJobStatus.COMPLETED:
        raise AppError(
            "Job is not in COMPLETED status, actual {job.status}", job_id=job_id
        )

    # raise Refactor
    if not job.agent_id:
        raise AppError("Job is detached from agent", job_id=job_id)

    agent_svc = TGAgentService(context.db_session)
    agent = await agent_svc.get(job.agent_id, with_bot=True)
    if not agent:
        raise AppError("Agent not found", job_id=job_id, agent_id=job.agent_id)
    if agent.tg_user_id != context.tg_user.tg_id:
        raise AppError(
            "Job is not created by the user",
            job_id=job_id,
            tg_user_id=context.tg_user.tg_id,
        )

    metadata = PostUpdateMetadata.model_validate(job.metadata_)
    # notify in bot
    await Bot(settings.TGBOT_TOKEN.get_secret_value()).send_message(
        chat_id=metadata.chat_id, text="Published"
    )

    # post in channel
    if metadata.photo_id:
        buffer = io.BytesIO()
        photo = await context.bot.get_file(metadata.photo_id)
        await photo.download_to_memory(buffer)
        buffer.seek(0)

        await Bot(agent.user_bot.api_token).send_photo(
            chat_id=agent.channel_id,
            photo=buffer,
            caption=metadata.original_message,
            parse_mode=ParseMode.HTML,
        )
    else:
        await Bot(agent.user_bot.api_token).send_message(
            chat_id=agent.channel_id,
            text=metadata.original_message,
            parse_mode=ParseMode.HTML,
        )

    # update channel_profile_generated
    asyncio.create_task(
        _update_channel_profile_generated(
            context.db_session_maker,
            agent.id,
            metadata.original_message,
        )
    )


@db_session
async def cancel_publish_post(update: Update, context: Context) -> None:
    print("cancel_publish_post")


@db_session
@requires_auth(is_admin=True)
async def generate_invites(update: Update, context: Context) -> None:
    logger.info("Generating invites by admin")
    # TODO: provide in context
    if not context.db_session:
        raise ValueError("DB session is None")
    if not context.tg_user:
        raise ValueError("TG user is None")

    if not context.tg_user.is_admin:
        logger.exception(
            "[CRITICAL] User is not admin accessed private endpoint - generate_invites",
            tg_user_id=context.tg_user.tg_id,
        )
        return

    invites_svc = TGInviteCodesService(context.db_session)
    invites = await invites_svc.create(
        amount=10, uses=1, tg_user_id=context.tg_user.tg_id, is_created_by_admin=True
    )

    chat = update.effective_chat
    if not chat:
        return

    invites_str = "\n".join(
        [
            f'{i + 1}. <a href="https://t.me/boostiq_bot?start={invite.code}">{invite.code}</a>'
            for i, invite in enumerate(invites)
        ]
    )
    message_text = f"<b>Invites:</b>\n\n{invites_str}"
    await chat.send_message(
        text=message_text,
        parse_mode=ParseMode.HTML,
    )


@db_session
@requires_auth(is_admin=True)
async def generate_invite_1(update: Update, context: Context) -> None:
    return await generate_invite(1, update, context)


@db_session
@requires_auth(is_admin=True)
async def generate_invite_10(update: Update, context: Context) -> None:
    return await generate_invite(1, update, context)


@db_session
@requires_auth(is_admin=True)
async def generate_invite_30(update: Update, context: Context) -> None:
    return await generate_invite(1, update, context)


async def generate_invite(uses: int, update: Update, context: Context) -> None:
    logger.info("Generating invite 1 by admin with {uses} uses")
    # TODO: provide in context
    if not context.db_session:
        raise ValueError("DB session is None")
    if not context.tg_user:
        raise ValueError("TG user is None")

    if not context.tg_user.is_admin:
        logger.exception(
            "[CRITICAL] User is not admin accessed private endpoint - generate_invites",
            tg_user_id=context.tg_user.tg_id,
        )
        return

    agent_job_svc = TGInviteCodesService(context.db_session)
    invites = await agent_job_svc.create(
        amount=1, uses=uses, tg_user_id=context.tg_user.tg_id, is_created_by_admin=True
    )

    chat = update.effective_chat
    if not chat:
        return

    invites_str = "\n".join(
        [
            f'{i + 1}. <a href="https://t.me/boostiq_bot?start={invite.code}">https://t.me/boostiq_bot?start={invite.code}</a>'
            for i, invite in enumerate(invites)
        ]
    )
    message_text = f"<b>Invites:</b>\n\n{invites_str}"
    await chat.send_message(
        text=message_text,
        parse_mode=ParseMode.HTML,
    )


async def _update_channel_profile_generated(
    db_session_maker: AsyncSessionMaker,
    agent_id: UUID,
    post_message: str,
) -> None:
    async with db_session_maker() as db_session:
        agent_svc = TGAgentService(db_session)
        tg_user_svc = TGUserService(db_session)

        agent = await agent_svc.get(agent_id)
        if not agent:
            raise AppError("Agent not found", agent_id=agent_id)
        if not agent.tg_user_id:
            raise AppError("Agent is orphaned", agent_id=agent_id)

        user = await tg_user_svc.get_user(agent.tg_user_id)
        if not user:
            raise AppError("User not found", tg_user_id=agent.tg_user_id)

        prompts = get_texts(PROMPTS, user.language_code)

        llm = get_llm("o4-mini")

        prompt_template = ChatPromptTemplate(
            [
                ("system", prompts.generate_channel_profile.system_prompt),
                (
                    "system",
                    prompts.generate_channel_profile.channel_profile_generated,
                ),
                ("user", prompts.generate_channel_profile.post_message),
            ]
        )

        messages = prompt_template.format_messages(
            channel_profile_generated=agent.channel_profile_generated,
            post_message=post_message,
        )
        result = await llm.ainvoke(messages)

        channel_profile_generated = result.content
        if channel_profile_generated:
            if not isinstance(channel_profile_generated, str):
                raise AppError(
                    "channel_profile_generated is not a string", agent_id=agent_id
                )

            await agent_svc.update_channel_profile_generated(
                agent_id, channel_profile_generated=channel_profile_generated
            )


UUID_PATTERN = r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[1-5][a-fA-F0-9]{3}-[89abAB][a-fA-F0-9]{3}-[a-fA-F0-9]{12}"

handlers = [
    CommandHandler("start", start),
    CommandHandler("generate_invites", generate_invites),
    CommandHandler("generate_invite_1", generate_invite_1),
    CommandHandler("generate_invite_10", generate_invite_10),
    CommandHandler("generate_invite_30", generate_invite_30),
    CallbackQueryHandler(publish_post, pattern=f"^/publish-post/({UUID_PATTERN})"),
    CallbackQueryHandler(
        cancel_publish_post, pattern=f"^/cancel-publish-post/({UUID_PATTERN})"
    ),
    MessageHandler(filters.TEXT & ~filters.COMMAND, process_request),
]
