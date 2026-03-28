import enum
import uuid
from datetime import datetime

# from uuid import UUID
from sqlalchemy import ARRAY, UUID, DateTime, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column

from flux_watch_api.schema.mixins.parent_mixin import ParentMixin
from flux_watch_api.schema.utils.base import Base


class AlertType(enum.Enum):
    ERROR_SPIKE = "ErrorSpike"


class AlertLevel(enum.Enum):
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    SEVERE = "SEVERE"


class AlertORM(Base, ParentMixin):
    __tablename__ = "alerts"

    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType), nullable=False)
    level: Mapped[AlertLevel] = mapped_column(Enum(AlertLevel), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    event_ids: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(UUID), nullable=False)
