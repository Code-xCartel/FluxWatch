from fastapi import APIRouter
from services.api.flux_watch_api.api.events.events import events_router
from services.api.flux_watch_api.api.health_check.health_check import (
    health_check_router,
)

router = APIRouter()

router.include_router(router=health_check_router, tags=["health"])
router.include_router(router=events_router, prefix="/events", tags=["events"])
