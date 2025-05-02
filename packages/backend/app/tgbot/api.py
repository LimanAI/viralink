from fastapi import APIRouter

from app.openapi import generate_unique_id_function
from app.tgbot.accounts.api import router as accounts_router

router = APIRouter(
    prefix="/tgbot",
    tags=["tgbot"],
)

router.include_router(accounts_router)
