from fastapi import APIRouter

from app.api.api_v1 import router as router_api_v1
from app.core.config import settings

api_router = APIRouter(
    prefix=settings.api.prefix,
)

api_router.include_router(router_api_v1)
