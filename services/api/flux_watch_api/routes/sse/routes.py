from fastapi import APIRouter

from flux_watch_api.routes.sse.events.events import sse_events_router

sse_router = APIRouter()

sse_router.include_router(router=sse_events_router, prefix="/events", tags=["events"])
