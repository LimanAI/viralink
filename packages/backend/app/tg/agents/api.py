from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from telegram import Bot
from telegram.error import TelegramError

from app.core.errors import AppError, ForbiddenError, NotFoundError
from app.core.http_errors import (
    HTTPForbiddenError,
    HTTPNotFoundError,
    HTTPUnauthorizedError,
)
from app.openapi import generate_unique_id_function
from app.tg.agents.bot import check_agent_bot_permissions
from app.tg.agents.models import BotMetadata
from app.tg.agents.schemas import (
    AddTGBotRequest,
    CreateTGAgentRequest,
    LinkTGBotRequest,
)
from app.tg.agents.schemas import TGAgent as TGAgentSchema
from app.tg.agents.schemas import TGUserBot as TGUserBotSchema
from app.tg.agents.services import TGAgentService
from app.tgbot.dependencies import AuthUser

logger = structlog.get_logger()

router = APIRouter(
    prefix="/agents",
    tags=["tg_agents"],
    generate_unique_id_function=generate_unique_id_function("tg::agents"),
    responses={401: {"model": HTTPUnauthorizedError}},
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    generate_unique_id_function=lambda *_: "tg::agents::list",
)
async def list_agents(
    user: AuthUser,
    agent_svc: Annotated[TGAgentService, Depends(TGAgentService.inject)],
) -> list[TGAgentSchema]:
    agents = await agent_svc.list_agents(tg_user_id=user.tg_id)
    return [TGAgentSchema.model_validate(agent) for agent in agents]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(
    user: AuthUser,
    data: CreateTGAgentRequest,
    agent_svc: Annotated[TGAgentService, Depends(TGAgentService.inject)],
) -> TGAgentSchema:
    agent = await agent_svc.create(
        tg_user_id=user.tg_id,
        channel_username=data.channel_username.lstrip("@"),
    )
    return TGAgentSchema.model_validate(agent)


@router.get(
    "/bots",
    status_code=status.HTTP_200_OK,
)
async def list_bots(
    user: AuthUser,
    agent_svc: Annotated[TGAgentService, Depends(TGAgentService.inject)],
) -> list[TGUserBotSchema]:
    bots = await agent_svc.list_bots(tg_user_id=user.tg_id)
    return [TGUserBotSchema.model_validate(bot) for bot in bots]


@router.get(
    "/{agent_id}",
    status_code=status.HTTP_200_OK,
    responses={404: {"model": HTTPNotFoundError}, 403: {"model": HTTPForbiddenError}},
)
async def get(
    user: AuthUser,
    agent_id: UUID,
    agent_svc: Annotated[TGAgentService, Depends(TGAgentService.inject)],
) -> TGAgentSchema:
    agent = await agent_svc.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    if agent.tg_user_id != user.tg_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access the agent",
        )
    return TGAgentSchema.model_validate(agent)


@router.post(
    "/{agent_id}/check-bot-permissions",
    status_code=status.HTTP_200_OK,
    responses={404: {"model": HTTPNotFoundError}},
)
async def check_bot_permissions(
    agent_id: UUID,
    user: AuthUser,
    agent_svc: Annotated[TGAgentService, Depends(TGAgentService.inject)],
) -> TGAgentSchema:
    """
    Long running endpoints that connects to the telegram and checks if the bot has sufficient permissions
    """
    try:
        agent = await check_agent_bot_permissions(user.tg_id, agent_id, agent_svc)
    except ForbiddenError as e:
        logger.exception(e)
        raise NotFoundError("Agent not found") from e
    except NotFoundError as e:
        raise NotFoundError("Agent not found") from e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking bot permissions",
        ) from e
    return TGAgentSchema.model_validate(agent)


@router.post(
    "/{agent_id}/bots",
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": HTTPNotFoundError}, 403: {"model": HTTPForbiddenError}},
)
async def createBot(
    agent_id: UUID,
    user: AuthUser,
    data: AddTGBotRequest,
    agent_svc: Annotated[TGAgentService, Depends(TGAgentService.inject)],
) -> TGAgentSchema:
    agent = await agent_svc.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    if agent.tg_user_id != user.tg_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to modify this agent",
        )

    try:
        bot = Bot(token=data.bot_token)
        bot_metadata = await bot.get_me()
    except TelegramError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid bot token",
        ) from e

    agent = await agent_svc.create_and_link_bot(
        agent_id,
        user.tg_id,
        data.bot_token,
        bot_metadata=BotMetadata.model_validate(bot_metadata),
    )
    return TGAgentSchema.model_validate(agent)


@router.post(
    "/{agent_id}/bots/link",
    status_code=status.HTTP_200_OK,
    responses={404: {"model": HTTPNotFoundError}},
)
async def link_bot(
    agent_id: UUID,
    user: AuthUser,
    data: LinkTGBotRequest,
    agent_svc: Annotated[TGAgentService, Depends(TGAgentService.inject)],
) -> TGAgentSchema:
    agent = await agent_svc.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    if agent.tg_user_id != user.tg_id:
        logger.exception(
            f"User {user.tg_id} tried to link bot {data.bot_id} to agent {agent_id} that belongs to user {agent.tg_user_id}",
            tg_user_id=user.tg_id,
            agent_id=agent_id,
            bot_id=data.bot_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    try:
        agent = await agent_svc.link_bot(agent.id, user.tg_id, data.bot_id)
    except ForbiddenError as e:
        logger.exception(str(e), **e.kwargs)
    except AppError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

    return TGAgentSchema.model_validate(agent)
