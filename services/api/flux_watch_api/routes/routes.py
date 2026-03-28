from fastapi import APIRouter

from flux_watch_api.routes.account.account import accounts_router
from flux_watch_api.routes.auth.api_keys import api_key_router
from flux_watch_api.routes.auth.auth import auth_router
from flux_watch_api.routes.events.events import events_router
from flux_watch_api.routes.health_check.health_check import (
    health_check_router,
)

router = APIRouter()

router.include_router(router=health_check_router, tags=["health"])
router.include_router(router=auth_router, prefix="/auth", tags=["auth"])
router.include_router(router=api_key_router, prefix="/keys", tags=["events"])
router.include_router(router=accounts_router, prefix="/account", tags=["events"])
router.include_router(router=events_router, prefix="/events", tags=["events"])
