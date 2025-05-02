from asyncio import iscoroutine
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession

from app.openapi import generate_unique_id_function
from app.tgbot.accounts.models import TGAccountStatus
from app.tgbot.accounts.schemas import (
    CodeRequest,
    CreateAccountRequest,
    SignInRequest,
    TGAccount,
)
from app.tgbot.accounts.services import TGAccountService

router = APIRouter(
    prefix="/accounts",
    tags=["tgbot_accounts"],
    generate_unique_id_function=generate_unique_id_function("tgbot::accounts"),
)


@router.post(
    "/",
    response_model=TGAccount,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"description": "Bad Request"}},
)
async def create(
    data: CreateAccountRequest,
    tg_account_svc: Annotated[TGAccountService, Depends(TGAccountService.inject)],
) -> TGAccount:
    try:
        tg_account_model = await tg_account_svc.create_account(data)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from None

    return TGAccount.model_validate(tg_account_model)


@router.post(
    "/send-code",
    response_model=TGAccount,
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Account not found"}},
)
async def send_code(
    data: CodeRequest,
    tg_account_svc: Annotated[TGAccountService, Depends(TGAccountService.inject)],
) -> TGAccount:
    tg_account_model = await tg_account_svc.get_account(data.api_id)

    if not tg_account_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    client = TelegramClient(
        StringSession(), tg_account_model.api_id, tg_account_model.api_hash
    )
    try:
        await client.connect()
        await client.send_code_request(data.phone_number)
    except Exception as e:
        await tg_account_svc.save_status_error(tg_account_model, {"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to send code"
        ) from None
    finally:
        disconnect = client.disconnect()
        if iscoroutine(disconnect):
            await disconnect

    async with tg_account_svc.tx():
        if data.phone_number != tg_account_model.phone_number:
            tg_account_model = await tg_account_svc.update_phone_number(
                tg_account_model, data.phone_number
            )
        tg_account_model = await tg_account_svc.update_status(
            tg_account_model, status=TGAccountStatus.SENT_CODE
        )

    return TGAccount.model_validate(tg_account_model)


@router.post(
    "/signin",
    response_model=TGAccount,
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Account not found"}},
)
async def signin(
    data: SignInRequest,
    tg_account_svc: Annotated[TGAccountService, Depends(TGAccountService.inject)],
) -> TGAccount:
    tg_account_model = await tg_account_svc.get_account(data.api_id)

    if not tg_account_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    session = StringSession()
    client = TelegramClient(session, tg_account_model.api_id, tg_account_model.api_hash)
    try:
        await client.connect()
        await client.sign_in(code=data.code, password=data.password or "")

        if not await client.is_user_authorized():
            raise Exception("User not authorized")

        # Save session string
        session_string = session.save()
        async with tg_account_svc.tx():
            tg_account_model = await tg_account_svc.save_session_string(
                tg_account_model, session_string
            )
            tg_account_model = await tg_account_svc.update_status(
                tg_account_model, status=TGAccountStatus.ACTIVE
            )
    except SessionPasswordNeededError:
        await tg_account_svc.save_status_error(
            tg_account_model, {"error": "2FA passowrd is required"}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="2FA password required"
        ) from None
    except Exception as e:
        await tg_account_svc.save_status_error(tg_account_model, {"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        ) from None
    finally:
        disconnect = client.disconnect()
        if iscoroutine(disconnect):
            await disconnect

    return TGAccount.model_validate(tg_account_model)
