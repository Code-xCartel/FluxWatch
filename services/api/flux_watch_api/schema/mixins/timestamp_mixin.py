from datetime import datetime

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from flux_watch_api.schema.utils.meta import MetaFields


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        MetaFields.CREATED_AT, TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        MetaFields.UPDATED_AT,
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
