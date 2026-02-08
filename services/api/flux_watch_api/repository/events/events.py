from fastapi import Depends

from flux_watch_api.core.base_repository import Repository
from flux_watch_api.database.query_builder.base import QueryModel
from flux_watch_api.database.query_builder.features import FilterFeature, ModelFeature
from flux_watch_api.models.events import Event
from flux_watch_api.models.response_schema import ListResponse, Meta
from flux_watch_api.schema.events import EventORM
from flux_watch_api.utils.orm_mapper import deserialize_events


class EventsSearch(QueryModel):
    features = [
        ModelFeature(EventORM),
        FilterFeature("event_id"),
    ]

    default_ordering = ["-occurred_at"]
    max_page_size = 100


class EventsRepository:
    def __init__(self, repo: Repository = Depends()):
        self.repo = repo

    def ingest_event(self, event: Event):
        return self.repo.add_one(event.serealize())

    def get_event_by_id(self, event_id: str) -> Event:
        raw_event = self.repo.get_one(EventsSearch, {"event_id": event_id})
        return deserialize_events(raw_event)

    def get_all_events(self, params) -> ListResponse[Event]:
        raw_events, total_count = self.repo.get_many(EventsSearch, params)
        events = [deserialize_events(event) for event in raw_events]
        return ListResponse(
            meta=Meta(total_count=total_count, returned_count=len(raw_events)),
            results=events,
        )
