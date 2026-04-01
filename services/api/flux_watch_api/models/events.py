from datetime import datetime
from typing import Any, Literal

from pydantic import Field, model_validator

from flux_watch_api.models.base import APIModel, ResourceModel

# Predetermined entity types for mvp
EntityType = Literal["user", "order", "system", "session"]

# Predetermined event types for each entity
EVENT_TYPES = {
    "user": ["user.login", "user.logout"],
    "order": ["order.created", "order.completed", "order.cancelled"],
    "system": ["system.metric"],
    "session": ["session.started", "session.ended"],
}


class EventEntity(APIModel):
    type: EntityType
    id: str


class EventActor(APIModel):
    type: str | None
    id: str | None


class EventContext(APIModel):
    trace_id: str | None
    session_id: str | None
    source: str | None  # e.g., "web", "mobile", "system"


class EventCreate(APIModel):
    entity: EventEntity
    event_type: str
    producer: str
    occurred_at: datetime
    actor: EventActor | None = None
    context: EventContext | None = None
    payload: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_event_type(self):
        valid_types = EVENT_TYPES.get(self.entity.type)
        if not valid_types or self.event_type not in valid_types:
            raise ValueError(
                f"Invalid event_type '{self.event_type}' for entity_type '{self.entity.type}'"
            )
        return self


class Event(EventCreate, ResourceModel):
    event_version: int
    parent: str
