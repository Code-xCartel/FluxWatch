from datetime import datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator
from services.api.flux_watch_api.schema.events import EventORM

# Predetermined entity types for mvp
EntityType = Literal["user", "order", "system", "session"]

# Predetermined event types for each entity
EVENT_TYPES = {
    "user": ["user.login", "user.logout"],
    "order": ["order.created", "order.completed", "order.cancelled"],
    "system": ["system.metric"],
    "session": ["session.started", "session.ended"],
}


class EventEntity(BaseModel):
    type: EntityType
    id: str


class EventActor(BaseModel):
    type: str | None
    id: str | None


class EventContext(BaseModel):
    trace_id: str | None
    session_id: str | None
    source: str | None  # e.g., "web", "mobile", "system"


class EventCreate(BaseModel):
    entity: EventEntity
    event_type: str
    producer: str
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


class Event(EventCreate):
    event_id: UUID = Field(default_factory=uuid4)
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    event_version: int = 1

    def serealize(self) -> EventORM:
        return EventORM(
            event_id=self.event_id,
            entity_type=self.entity.type,
            entity_id=self.entity.id,
            event_type=self.event_type,
            event_version=self.event_version,
            occurred_at=self.occurred_at,
            producer=self.producer,
            actor_type=self.actor.type if self.actor else None,
            actor_id=self.actor.id if self.actor else None,
            context=self.context.model_dump() if self.context else None,
            payload=self.payload,
        )

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "uuid",
                "entity": {"type": "user", "id": "USR_1"},
                "event_type": "user.login",
                "event_version": 1,
                "occurred_at": "2026-02-07T12:00:00Z",
                "producer": "frontend-app",
                "actor": {"type": "user", "id": "USR_1"},
                "context": {
                    "trace_id": "req-123",
                    "session_id": "sess-456",
                    "source": "web",
                },
                "payload": {"ip": "1.2.3.4", "device": "web"},
            }
        }
