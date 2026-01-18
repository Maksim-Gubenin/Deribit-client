from fastapi import APIRouter

from app.api.api_v1.deribits.deribit_routes import router as deribit_router
from app.core.config import settings

router = APIRouter(
    prefix=settings.api.v1.prefix,
)
router.include_router(deribit_router, prefix=settings.api.v1.deribit, tags=["Deribit"])
