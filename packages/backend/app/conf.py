from enum import Enum
from pathlib import Path
from typing import Literal, cast

import tomllib
from pydantic import HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(str, Enum):
    dev = "dev"
    prod = "prod"
    test = "test"


def get_version() -> str:
    with open(Path(__file__).parent.parent / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        return cast(str, data["tool"]["poetry"]["version"])


class JWTSettings(BaseSettings):
    issuer: str = "ViraLink AI"
    algorithm: Literal["HS512"] = "HS512"
    access_token_expire_minutes: int = 60
    access_token_renewal_leeway_days: int = 3
    refresh_token_expire_days: int = 7


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )

    VERSION: str = get_version()
    ENV: Env = Env.dev
    DEBUG: bool = False
    DEBUG_SQL: bool = False

    WEBAPP_URL: str

    # Required
    SECRET_KEY: SecretStr
    DATABASE_URL: SecretStr
    REDIS_URL: SecretStr
    TGBOT_TOKEN: SecretStr
    OPENAI_API_KEY: SecretStr
    REPLICATE_API_KEY: SecretStr
    # Required -- Storage
    STORAGE_URL: HttpUrl
    STORAGE_BUCKET: str
    STORAGE_ACCESS_KEY: SecretStr
    STORAGE_SECRET_KEY: SecretStr

    # Optional
    TGBOT_POOLING: bool = True
    TGBOT_SETUP_COMMANDS: bool = False
    TGBOT_REQUIRES_INVITE: bool = False
    CORS_ALLOW_ORIGINS: list[str] = []
    LOGFIRE_TOKEN: SecretStr | None = None

    # JWT
    JWT: JWTSettings = JWTSettings()


# https://github.com/pydantic/pydantic/issues/3753
settings = Settings.model_validate({})
