import logging
from typing import Any, TypeVar

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from flux_watch_api.database.query_builder.base import QueryModel
from flux_watch_api.database.query_builder.builder import QueryBuilder
from flux_watch_api.database.session import InjectSession
from flux_watch_api.errors.rest_errors import AlreadyExistsError, NotFoundError

T = TypeVar("T")

logger = logging.getLogger(__name__)


class SQLClient:
    def __init__(self, session: Session = InjectSession()):
        self.session = session

    def add_one(self, obj: Any):
        try:
            self.session.add(obj)
            self.session.flush()
            self.session.refresh(obj)
            return obj
        except IntegrityError as err:
            raise AlreadyExistsError from err

    def get_one(self, search_model: QueryModel, params) -> T | None:
        builder = QueryBuilder(search_model, params)
        query, _ = builder.build(paginate=False, sort=False)
        logger.info(f"executing query: {query}")
        result = self.session.execute(query).scalar_one_or_none()
        if not result:
            raise NotFoundError
        return result

    def get_many(self, search_model: QueryModel, params) -> T | None:
        builder = QueryBuilder(search_model, params)
        data_query, count_query = builder.build(with_counts=True)
        logger.info(f"executing query: {data_query}")
        rows = self.session.execute(data_query).scalars().all()
        total_count = self.session.execute(count_query).scalar_one()
        return rows, total_count
