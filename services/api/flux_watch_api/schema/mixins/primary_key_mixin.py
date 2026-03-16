from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from flux_watch_api.schema.utils.meta import MetaFields


class UUIDPrimaryKeyMixin:
    id: Mapped[UUID] = mapped_column(
        MetaFields.ID, PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
