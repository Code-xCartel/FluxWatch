from fastapi import Depends

from flux_watch_api.core.base_repository import Repository
from flux_watch_api.models.events import Event
from flux_watch_api.schema.events import EventORM
from flux_watch_api.utils.orm_mapper import deserialize_events


class EventsRepository:
    def __init__(self, repo: Repository = Depends()):
        self.repo = repo

    def ingest_event(self, event: Event):
        return self.repo.add_one(event.serealize())

    def get_event_by_id(self, event_id: str) -> Event:
        raw_event = self.repo.get_one(EventORM, event_id=event_id)
        return deserialize_events(raw_event)
