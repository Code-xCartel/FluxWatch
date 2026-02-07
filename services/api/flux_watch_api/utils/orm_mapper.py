from services.api.flux_watch_api.models.events import (
    Event,
    EventActor,
    EventContext,
    EventEntity,
)
from services.api.flux_watch_api.schema.events import EventORM


# need this mapper since adding Event based deserialization causes circular dependency
def deserialize_events(obj: EventORM) -> Event:
    return Event(
        event_id=obj.event_id,
        entity=EventEntity(type=obj.entity_type, id=obj.entity_id),
        event_type=obj.event_type,
        event_version=obj.event_version,
        occurred_at=obj.occurred_at,
        producer=obj.producer,
        actor=EventActor(type=obj.actor_type, id=obj.actor_id)
        if obj.actor_type or obj.actor_id
        else None,
        context=EventContext(**obj.context) if obj.context else None,
        payload=obj.payload or {},
    )
