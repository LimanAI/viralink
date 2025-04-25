from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.conf import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        yield
    finally:
        ...


app = FastAPI(
    version=settings.VERSION,
    lifespan=lifespan,
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": f"ViraLink v{settings.VERSION}"}
