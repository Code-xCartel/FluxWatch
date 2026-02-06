from datetime import datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

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


class EventPayload(BaseModel):
    __root__: dict[str, Any]  # Generic payload; can validate per event_type later


class Event(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    entity: EventEntity
    event_type: str
    event_version: int = 1
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    producer: str  # service emitting the event
    actor: EventActor | None = None
    context: EventContext | None = None
    payload: EventPayload = Field(default_factory=dict)

    # Ensure event_type matches entity.type
    @model_validator(mode="after")
    def validate_event_type(cls, values):
        entity = values.get("entity")
        event_type = values.get("event_type")
        if entity and event_type:
            valid_types = EVENT_TYPES.get(entity.type)
            if not valid_types or event_type not in valid_types:
                raise ValueError(
                    f"Invalid event_type '{event_type}' for entity_type '{entity.type}'"
                )
        return values

    class Config:
        schema_extra = {
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
