from fastapi import APIRouter

from core.config import settings

from .api_v1 import router_api_v1


router_api = APIRouter(
    prefix=settings.api.prefix,
)


router_api.include_router(router_api_v1)
