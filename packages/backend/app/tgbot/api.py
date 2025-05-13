from fastapi import APIRouter

from app.tgbot.auth.api import router as auth_router

router = APIRouter(
    prefix="/tgbot",
    tags=["tgbot"],
)

router.include_router(auth_router)
