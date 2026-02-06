from fastapi import APIRouter
from services.api.flux_watch_api.api.health_check.health_check import (
    health_check_router,
)

router = APIRouter()

router.include_router(router=health_check_router)
