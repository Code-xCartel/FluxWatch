from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column

from flux_watch_api.schema.utils.meta import MetaFields


class SoftDeleteMixin:
    expired: Mapped[bool] = mapped_column(
        MetaFields.EXPIRED, Boolean, default=False, nullable=False
    )
