from typing import Any, TypeVar

from fastapi import Depends
from sqlalchemy.orm import Session

from flux_watch_api.database.query_builder.base import QueryModel
from flux_watch_api.database.query_builder.builder import QueryBuilder
from flux_watch_api.database.session import get_session

T = TypeVar("T")


class SQLClient:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def add_one(self, obj: Any):
        self.session.add(obj)
        return obj

    def get_one(self, search_model: QueryModel, params) -> T | None:
        builder = QueryBuilder(search_model, params)
        query = builder.build(paginate=False, sort=False)
        result = self.session.execute(query).scalar_one_or_none()
        return result

    def get_many(self, search_model: QueryModel, params) -> T | None:
        builder = QueryBuilder(search_model, params)
        data_query, count_query = builder.build(with_counts=True)
        rows = self.session.execute(data_query).scalars().all()
        total_count = self.session.execute(count_query).scalar_one()
        return rows, total_count
