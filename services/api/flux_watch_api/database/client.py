import logging
from typing import Any, TypeVar

from sqlalchemy.orm import Session

from flux_watch_api.database.query_builder.base import QueryModel
from flux_watch_api.database.query_builder.builder import QueryBuilder
from flux_watch_api.database.session import InjectSession

T = TypeVar("T")

logger = logging.getLogger(__name__)


class SQLClient:
    def __init__(self, session: Session = InjectSession()):
        self.session = session

    def add_one(self, obj: Any):
        self.session.add(obj)
        return obj

    def get_one(self, search_model: QueryModel, params) -> T | None:
        builder = QueryBuilder(search_model, params)
        query = builder.build(paginate=False, sort=False)
        logger.info(f"executing query: {query}")
        result = self.session.execute(query).scalar_one_or_none()
        return result

    def get_many(self, search_model: QueryModel, params) -> T | None:
        builder = QueryBuilder(search_model, params)
        data_query, count_query = builder.build(with_counts=True)
        logger.info(f"executing query: {data_query}")
        rows = self.session.execute(data_query).scalars().all()
        total_count = self.session.execute(count_query).scalar_one()
        return rows, total_count
