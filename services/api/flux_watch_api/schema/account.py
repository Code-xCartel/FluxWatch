from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flux_watch_api.schema.session import AccountSessionORM
from flux_watch_api.schema.utils.base import Base

if TYPE_CHECKING:
    from flux_watch_api.schema.account_creds import AccountCredsORM


class AccountORM(Base):
    __tablename__ = "account"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    principal: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)

    credentials: Mapped["AccountCredsORM"] = relationship(
        "AccountCredsORM", back_populates="account", uselist=False, cascade="all, delete-orphan"
    )

    sessions: Mapped[list["AccountSessionORM"]] = relationship(
        "AccountSessionORM", back_populates="account", cascade="all, delete-orphan"
    )
