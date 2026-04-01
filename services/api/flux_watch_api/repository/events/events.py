from typing import cast

from fastapi import Depends

from flux_watch_api.core.base_repository import Repository
from flux_watch_api.database.query_builder.base import QueryModel
from flux_watch_api.database.query_builder.features import FilterFeature, ModelFeature
from flux_watch_api.models.events import Event, EventCreate
from flux_watch_api.models.response_schema import ListResponse, Meta
from flux_watch_api.schema.events import EventORM
from flux_watch_api.schema.utils.meta import MetaFields
from flux_watch_api.utils.constants import REDIS_EVENT_PROCESSOR_KEY


class EventsSearch(QueryModel):
    features = [
        ModelFeature(EventORM),
        FilterFeature(field=MetaFields.ID),
        FilterFeature(field=MetaFields.PARENT),
    ]

    default_ordering = ["-occurred_at"]
    max_page_size = 100


class EventsRepository:
    def __init__(self, repo: Repository = Depends()):
        self.repo = repo

    def ingest_event(self, event: EventCreate) -> Event:
        serialized_event = EventORM.from_model(event, parent=self.repo.session_account.principal)
        result: EventORM = self.repo.add_one(serialized_event)

        self.repo.publish(REDIS_EVENT_PROCESSOR_KEY, result.to_stream_message())

        return result.to_model()

    def get_event_by_id(self, event_id: str) -> Event:
        raw_event: EventORM = self.repo.get_one(EventsSearch, {"id": event_id})
        return raw_event.to_model()

    def get_all_events(self, params) -> ListResponse[Event]:
        raw_events, total_count = cast(
            tuple[list[EventORM], int], self.repo.get_many(EventsSearch, params)
        )
        return ListResponse(
            meta=Meta(total_count=total_count, returned_count=len(raw_events)),
            results=[event.to_model() for event in raw_events],
        )
