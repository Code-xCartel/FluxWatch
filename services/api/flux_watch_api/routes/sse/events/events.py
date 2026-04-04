from fastapi import APIRouter, Depends, Request
from starlette import status

from flux_watch_api.models.query import Query
from flux_watch_api.repository.events.events import EventsRepository
from flux_watch_api.repository.sse.sse import ServerSentEvents

sse_events_router = APIRouter()


@sse_events_router.get("", status_code=status.HTTP_200_OK)
async def get_events(
    request: Request,
    query_params: Query = Depends(),
    sse: ServerSentEvents = Depends(),
    repo: EventsRepository = Depends(),
):
    return await sse.stream(
        fn=repo.get_all_events,
        args={
            **query_params.as_dict(),
        },
        request=request,
    )
