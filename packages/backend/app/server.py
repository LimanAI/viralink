from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TypedDict

from fastapi import FastAPI

from app.auth.api import router as auth_router
from app.conf import settings
from app.db import create_async_engine, create_session_maker
from app.openapi import configure_openapi, generate_unique_id_function
from app.tgbot.app import TGApp
from app.tgbot.main import start_tg_app


class AppState(TypedDict):
    tg_app: TGApp


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[AppState, None]:
    engine = create_async_engine(settings.DATABASE_URL, "app")
    session_maker = create_session_maker(engine)

    try:
        async with start_tg_app(session_maker) as tg_app:
            yield AppState(tg_app=tg_app)
    finally:
        ...


app = FastAPI(
    version=settings.VERSION,
    lifespan=lifespan,
    generate_unique_id_function=generate_unique_id_function(),
)

app.include_router(auth_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": f"ViraLink v{settings.VERSION}"}


configure_openapi(app)
