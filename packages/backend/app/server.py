from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TypedDict

from fastapi import FastAPI

from app.conf import settings
from app.tgbot.main import TGApp, start_tg_app


class AppState(TypedDict):
    tg_app: TGApp


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[AppState, None]:
    try:
        async with start_tg_app() as tg_app:
            yield AppState(tg_app=tg_app)
    finally:
        ...


app = FastAPI(
    version=settings.VERSION,
    lifespan=lifespan,
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": f"ViraLink v{settings.VERSION}"}
