from enum import Enum
from pathlib import Path
from typing import cast

import tomllib
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(str, Enum):
    dev = "dev"
    prod = "prod"
    test = "test"


def get_version() -> str:
    with open(Path(__file__).parent.parent / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        return cast(str, data["tool"]["poetry"]["version"])


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )

    VERSION: str = get_version()
    ENV: Env = Env.dev
    DEBUG: bool = False

    # Required
    DATABASE_URL: SecretStr


# https://github.com/pydantic/pydantic/issues/3753
settings = Settings.model_validate({})
