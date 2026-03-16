from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import TIMESTAMP, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flux_watch_api.schema.utils.base import Base

if TYPE_CHECKING:
    from flux_watch_api.schema.account import AccountORM


class AccountSessionORM(Base):
    __tablename__ = "account_session"

    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    session_token: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    ttl: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    account: Mapped["AccountORM"] = relationship("AccountORM", back_populates="sessions")
