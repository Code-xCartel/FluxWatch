import json
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from flux_watch_api.models.events import Event, EventActor, EventContext, EventEntity
from flux_watch_api.schema.mixins.parent_mixin import ParentMixin
from flux_watch_api.schema.utils.base import Base


class EventORM(Base, ParentMixin):
    __tablename__ = "events"

    entity_type: Mapped[str] = mapped_column(Text, nullable=False)
    entity_id: Mapped[str] = mapped_column(Text, nullable=False)

    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    event_version: Mapped[int] = mapped_column(Integer, default=1)

    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    producer: Mapped[str] = mapped_column(Text, nullable=False)

    actor_type: Mapped[str | None] = mapped_column(Text)
    actor_id: Mapped[str | None] = mapped_column(Text)

    context: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    def to_model(self):
        return Event(
            id=self.id,
            entity=EventEntity(type=self.entity_type, id=self.entity_id),  # type: ignore[arg-type]
            event_type=self.event_type,
            event_version=self.event_version,
            occurred_at=self.occurred_at,
            producer=self.producer,
            actor=EventActor(type=self.actor_type, id=self.actor_id)
            if self.actor_type or self.actor_id
            else None,
            context=EventContext(**self.context) if self.context else None,
            payload=self.payload or {},
            parent=self.parent,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def to_stream_message(self) -> dict[str, str]:
        """Serialize to a flat string dict for publishing to a Redis stream."""
        return {
            "event_id": str(self.id),
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "event_type": self.event_type,
            "event_version": str(self.event_version),
            "occurred_at": self.occurred_at.isoformat(),
            "producer": self.producer,
            "actor_type": self.actor_type or "",
            "actor_id": self.actor_id or "",
            "context": json.dumps(self.context) if self.context else "",
            "payload": json.dumps(self.payload) if self.payload else "{}",
            "parent": self.parent,
        }

    @classmethod
    def from_model(cls, event: Any, parent: str) -> "EventORM":
        return cls(
            entity_type=event.entity.type,
            entity_id=event.entity.id,
            event_type=event.event_type,
            event_version=1,
            occurred_at=event.occurred_at,
            producer=event.producer,
            actor_type=event.actor.type if event.actor else None,
            actor_id=event.actor.id if event.actor else None,
            context=event.context.model_dump() if event.context else None,
            payload=event.payload,
            parent=parent,
        )
