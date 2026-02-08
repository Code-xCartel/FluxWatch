from fastapi import APIRouter, Depends
from starlette import status

from flux_watch_api.models.events import Event, EventCreate
from flux_watch_api.models.query import Query
from flux_watch_api.models.response_schema import ListResponse
from flux_watch_api.repository.events.events import EventsRepository

events_router = APIRouter()


@events_router.post("/ingest", tags=["ingest"], status_code=status.HTTP_201_CREATED)
def ingest(event: EventCreate, repo: EventsRepository = Depends()):
    return repo.ingest_event(Event(**event.model_dump()))


@events_router.get(
    "/{event_id}", tags=["events"], status_code=status.HTTP_200_OK, response_model=Event
)
def get_event(event_id: str, repo: EventsRepository = Depends()):
    return repo.get_event_by_id(event_id)


@events_router.get(
    "", tags=["events"], status_code=status.HTTP_200_OK, response_model=ListResponse[Event]
)
def get_events(query_params: Query = Depends(), repo: EventsRepository = Depends()):
    return repo.get_all_events(query_params.as_dict())
