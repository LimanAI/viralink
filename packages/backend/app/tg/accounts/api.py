from asyncio import iscoroutine
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession

from app.auth.dependencies import AuthAdmin
from app.core.http_errors import HTTPError
from app.models.base import ErrorSchema
from app.openapi import generate_unique_id_function
from app.tg.accounts.models import TGAccountStatus
from app.tg.accounts.schemas import (
    CodeRequest,
    CreateAccountRequest,
    SignInRequest,
    TGAccount,
)
from app.tg.accounts.services import TGAccountService

logger = structlog.get_logger()

router = APIRouter(
    prefix="/accounts",
    tags=["tg_accounts"],
    generate_unique_id_function=generate_unique_id_function("tg::accounts"),
)


@router.post(
    "/",
    response_model=TGAccount,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": HTTPError}},
)
async def create(
    _: AuthAdmin,
    data: CreateAccountRequest,
    tg_account_svc: Annotated[TGAccountService, Depends(TGAccountService.inject)],
) -> TGAccount:
    try:
        tg_account_model = await tg_account_svc.create_account(data)
    except Exception as e:
        logger.exception(f"Error creating account: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request"
        ) from None

    return TGAccount.model_validate(tg_account_model)


@router.post(
    "/send-code",
    response_model=TGAccount,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": HTTPError}},
)
async def send_code(
    _: AuthAdmin,
    data: CodeRequest,
    tg_account_svc: Annotated[TGAccountService, Depends(TGAccountService.inject)],
) -> TGAccount:
    tg_account_model = await tg_account_svc.get_account(data.account_id)

    if not tg_account_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    session = StringSession()
    client = TelegramClient(session, tg_account_model.api_id, tg_account_model.api_hash)
    try:
        await client.connect()
        result = await client.send_code_request(data.phone_number)

        # Save session string
        session_string = session.save()
        async with tg_account_svc.tx():
            await tg_account_svc.save_session_string(
                tg_account_model.id, session_string
            )
            await tg_account_svc.update_phone_number(
                tg_account_model.id, data.phone_number, result.phone_code_hash
            )
            tg_account_model = await tg_account_svc.update_status(
                tg_account_model.id, status=TGAccountStatus.SENT_CODE
            )
    except Exception as e:
        logger.exception(f"Error sent_code in: {e}")
        await tg_account_svc.save_status_error(
            tg_account_model.id, ErrorSchema(message=str(e))
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to send code"
        ) from None
    finally:
        disconnect = client.disconnect()
        if iscoroutine(disconnect):
            await disconnect

    return TGAccount.model_validate(tg_account_model)


@router.post(
    "/signin",
    response_model=TGAccount,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": HTTPError}, 400: {"model": HTTPError}},
)
async def signin(
    _: AuthAdmin,
    data: SignInRequest,
    tg_account_svc: Annotated[TGAccountService, Depends(TGAccountService.inject)],
) -> TGAccount:
    tg_account_model = await tg_account_svc.get_account(data.account_id)

    if not tg_account_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    session = StringSession(tg_account_model.session_string)
    client = TelegramClient(session, tg_account_model.api_id, tg_account_model.api_hash)
    try:
        await client.connect()
        await client.sign_in(
            code=data.code,
            phone=tg_account_model.phone_number,
            phone_code_hash=tg_account_model.phone_code_hash,
        )

        if not await client.is_user_authorized():
            raise Exception("User not authorized")

    except SessionPasswordNeededError:
        if not data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="2FA password required"
            ) from None

        await client.sign_in(password=data.password)
        if not await client.is_user_authorized():
            raise Exception("User not authorized") from None
    except Exception as e:
        logger.exception(f"Error signing in: {e}")
        await tg_account_svc.save_status_error(
            tg_account_model.id, ErrorSchema(message=str(e))
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        ) from None
    finally:
        disconnect = client.disconnect()
        if iscoroutine(disconnect):
            await disconnect

    # Save session string
    session_string = session.save()
    async with tg_account_svc.tx():
        await tg_account_svc.save_session_string(tg_account_model.id, session_string)
        tg_account_model = await tg_account_svc.update_status(
            tg_account_model.id, status=TGAccountStatus.ACTIVE
        )

    return TGAccount.model_validate(tg_account_model)


@router.get(
    "/{account_id}",
    response_model=TGAccount,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": HTTPError}},
)
async def get(
    _: AuthAdmin,
    tg_account_svc: Annotated[TGAccountService, Depends(TGAccountService.inject)],
    account_id: UUID,
) -> TGAccount:
    tg_account_model = await tg_account_svc.get_account(account_id)

    if not tg_account_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )
    return TGAccount.model_validate(tg_account_model)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    generate_unique_id_function=lambda *_: "tg::accounts::list",
)
async def list_accounts(
    _: AuthAdmin,
    tg_account_svc: Annotated[TGAccountService, Depends(TGAccountService.inject)],
) -> list[TGAccount]:
    tg_account_models = await tg_account_svc.list()

    return [
        TGAccount.model_validate(tg_account_model)
        for tg_account_model in tg_account_models
    ]
