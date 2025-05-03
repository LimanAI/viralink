from fastapi import APIRouter

from app.tg.accounts.api import router as accounts_router

router = APIRouter(
    prefix="/tg",
    tags=["tg"],
)

router.include_router(accounts_router)
