from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import AuthAdmin
from app.openapi import generate_unique_id_function
from app.tgbot.auth.models import TGUser
from app.tgbot.auth.schemas import CreateTGInviteCodes
from app.tgbot.auth.schemas import TGInviteCode as TGInviteCodeSchema
from app.tgbot.auth.schemas import TGUser as TGUserSchema
from app.tgbot.auth.services import TGInviteCodesService
from app.tgbot.dependencies import AuthUser

router = APIRouter(
    prefix="/auth",
    tags=["tgbot_auth"],
    generate_unique_id_function=generate_unique_id_function("tgbot::auth"),
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def me(
    user: AuthUser,
) -> TGUserSchema:
    return TGUserSchema.model_validate(user)


# disabled routes
if False:

    @router.put(
        "/invite_codes",
        response_model=list[TGInviteCodeSchema],
        status_code=status.HTTP_201_CREATED,
    )
    async def create_invite_codes(
        auth: AuthAdmin,
        data: CreateTGInviteCodes,
        invite_codes_svc: Annotated[
            TGInviteCodesService, Depends(TGInviteCodesService.inject)
        ],
    ) -> list[TGInviteCodeSchema]:
        invite_codes = await invite_codes_svc.create(
            amount=data.amount, uses=data.uses, is_created_by_admin=True
        )
        return [
            TGInviteCodeSchema.model_validate(invite_code)
            for invite_code in invite_codes
        ]
