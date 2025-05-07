from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.http_errors import HTTPUnauthorizedError
from app.openapi import generate_unique_id_function
from app.tg.agents.schemas import CreateTGAgentRequest, TGAgentSchema
from app.tg.agents.services import TGAgentService
from app.tgbot.dependencies import AuthUser

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
    agents = await agent_svc.list(tg_user_id=user.tg_id)
    return [TGAgentSchema.model_validate(agent) for agent in agents]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(
    user: AuthUser,
    data: CreateTGAgentRequest,
    agent_svc: Annotated[TGAgentService, Depends(TGAgentService.inject)],
) -> TGAgentSchema:
    agent = await agent_svc.create(
        tg_user_id=user.tg_id,
        channel_link=data.channel_link,
    )
    return TGAgentSchema.model_validate(agent)
