from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flux_watch_api.schema.utils.base import Base

if TYPE_CHECKING:
    from flux_watch_api.schema.account import AccountORM


class AccountCredsORM(Base):
    __tablename__ = "account_creds"

    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)

    account: Mapped["AccountORM"] = relationship("AccountORM", back_populates="credentials")
