from datetime import timedelta
from uuid import UUID

from authlib.jose import jwt

from app.conf import settings
from app.models.base import utc_now


def generate_jwt(
    user_id: UUID,
    is_admin: bool = False,
    expires_in: timedelta = timedelta(minutes=settings.JWT.access_token_expire_minutes),
) -> str:
    header = {"alg": settings.JWT.algorithm, "typ": "JWT"}
    payload = {
        "iss": settings.JWT.issuer,
        "sub": str(user_id),
        "exp": utc_now() + expires_in,
        "iat": utc_now(),
        "is_admin": is_admin,
    }
    b = jwt.encode(header, payload, settings.SECRET_KEY.get_secret_value())
    if not isinstance(b, bytes):
        raise ValueError("jwt.encode() must return bytes")
    return b.decode("utf-8")
