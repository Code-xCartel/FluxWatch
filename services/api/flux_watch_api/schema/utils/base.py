from sqlalchemy.orm import DeclarativeBase

from flux_watch_api.schema.mixins.primary_key_mixin import UUIDPrimaryKeyMixin
from flux_watch_api.schema.mixins.soft_delete_mixin import SoftDeleteMixin
from flux_watch_api.schema.mixins.timestamp_mixin import TimestampMixin


class Base(DeclarativeBase, UUIDPrimaryKeyMixin, SoftDeleteMixin, TimestampMixin):
    __abstract__ = True
