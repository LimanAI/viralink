from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.auth.dependencies import Auth, AuthExp, AuthOrAnonym
from app.auth.errors import AuthError, EmailAlreadyRegisteredError
from app.auth.schemas import (
    AccessToken,
    SignInRequest,
    SignUpRequest,
    User,
)
from app.auth.services import AuthService, UserService
from app.auth.utils import generate_jwt
from app.conf import settings
from app.core.http_errors import HTTPError, HTTPUnauthorizedError
from app.openapi import generate_unique_id_function

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    generate_unique_id_function=generate_unique_id_function("auth"),
)

logger = structlog.get_logger()


@router.post(
    "/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": HTTPError}},
)
async def signup(
    data: SignUpRequest,
    auth_svc: Annotated[AuthService, Depends(AuthService.inject)],
) -> User:
    try:
        user = await auth_svc.signup_with_password(data)
    except EmailAlreadyRegisteredError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from e

    return User.model_validate(user)


@router.post(
    "/signin",
    response_model=AccessToken,
    responses={401: {"model": HTTPUnauthorizedError}},
)
async def signin(
    data: SignInRequest,
    request: Request,
    response: Response,
    auth_svc: Annotated[AuthService, Depends(AuthService.inject)],
) -> AccessToken:
    try:
        access_token, refresh_token = await auth_svc.signin_with_password(
            data.email,
            data.password,
            user_agent=request.headers.get("User-Agent"),
            ip_addr=request.client.host if request.client else None,
        )
    except AuthError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        max_age=settings.JWT.refresh_token_expire_days * 24 * 60 * 60,
    )
    return AccessToken(token=access_token)


@router.post("/refresh-token", response_model=AccessToken)
async def refresh_token(
    auth: AuthExp,
    request: Request,
    response: Response,
    user_svc: Annotated[UserService, Depends(UserService.inject)],
) -> AccessToken:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # use access_token as csrf token
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid access token",
    )
    if not auth.access_token.can_renew:
        raise exception

    session = await user_svc.get_session_by_token(refresh_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if auth.user_id != session.user_id:
        logger.critical(f"User {auth.user_id} uses session for {session.user_id}")
        raise exception

    # update refresh token if it's about to expire
    if session.is_expiring_soon:
        new_session = await user_svc.renew_session(
            session,
            user_agent=request.headers.get("User-Agent"),
            ip_addr=request.client.host if request.client else None,
        )
        response.set_cookie(
            "refresh_token",
            new_session.refresh_token,
            httponly=True,
            max_age=settings.JWT.refresh_token_expire_days * 24 * 60 * 60,
        )

    jwt_token = generate_jwt(session.user_id)
    return AccessToken(token=jwt_token)


@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT)
async def signout(
    _: AuthOrAnonym,
    request: Request,
    response: Response,
    user_svc: Annotated[UserService, Depends(UserService.inject)],
) -> Response:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    await user_svc.revoke_session(refresh_token)
    response.delete_cookie(
        "refresh_token",
        httponly=True,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=User)
async def get_current_user(
    auth: Auth,
    user_svc: Annotated[UserService, Depends(UserService.inject)],
) -> User:
    user = await user_svc.get_user(auth.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return User.model_validate(user)
