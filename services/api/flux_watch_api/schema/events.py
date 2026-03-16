from typing import Any

from sqlalchemy import Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from flux_watch_api.schema.utils.base import Base


class EventORM(Base):
    __tablename__ = "events"

    entity_type: Mapped[str] = mapped_column(Text, nullable=False)
    entity_id: Mapped[str] = mapped_column(Text, nullable=False)

    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    event_version: Mapped[int] = mapped_column(Integer, default=1)

    producer: Mapped[str] = mapped_column(Text, nullable=False)

    actor_type: Mapped[str | None] = mapped_column(Text)
    actor_id: Mapped[str | None] = mapped_column(Text)

    context: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
