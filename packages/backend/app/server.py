from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TypedDict

import logfire
from arq.connections import ArqRedis, create_pool
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.api import router as auth_router
from app.conf import settings
from app.db import AsyncSessionMaker, create_async_engine, create_session_maker
from app.logging import configure_logging
from app.openapi import configure_openapi, generate_unique_id_function
from app.tg.api import router as tg_router
from app.tgbot.api import router as tgbot_router
from app.tgbot.app import TGApp
from app.tgbot.main import start_tg_app
from app.worker.conf import WorkerSettings


class AppState(TypedDict):
    tg_app: TGApp
    session_maker: AsyncSessionMaker
    arq: ArqRedis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[AppState, None]:
    engine = create_async_engine(settings.DATABASE_URL, "app")
    session_maker = create_session_maker(engine)
    arq = await create_pool(
        WorkerSettings.redis_settings, default_queue_name=WorkerSettings.queue_name
    )

    try:
        async with start_tg_app(session_maker) as tg_app:
            yield AppState(tg_app=tg_app, session_maker=session_maker, arq=arq)
    finally:
        ...


app = FastAPI(
    version=settings.VERSION,
    lifespan=lifespan,
    generate_unique_id_function=generate_unique_id_function(),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tg_router)
app.include_router(tgbot_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": f"ViraLink v{settings.VERSION}"}


configure_logging(name="api")
if settings.LOGFIRE_TOKEN:
    logfire.instrument_fastapi(app, capture_headers=False)
configure_openapi(app)
