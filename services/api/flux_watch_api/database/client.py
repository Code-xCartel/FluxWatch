from typing import Any, TypeVar

from fastapi import Depends
from services.api.flux_watch_api.database.session import get_session
from sqlalchemy import select
from sqlalchemy.orm import Session

T = TypeVar("T")


class SQLClient:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def add_one(self, obj: Any):
        self.session.add(obj)
        return obj

    def get_one(self, model: type[T], **filters) -> T | None:
        stmt = select(model).filter_by(**filters)
        result = self.session.execute(stmt).scalar_one_or_none()
        return result
