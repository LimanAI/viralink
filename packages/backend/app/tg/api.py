from fastapi import APIRouter

from app.tg.accounts.api import router as accounts_router
from app.tg.agents.api import router as agents_router

router = APIRouter(
    prefix="/tg",
    tags=["tg"],
)

router.include_router(accounts_router)
router.include_router(agents_router)
