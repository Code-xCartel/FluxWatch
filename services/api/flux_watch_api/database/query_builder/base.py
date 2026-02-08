from abc import ABC, abstractmethod

from sqlalchemy.sql import Select


class QueryModel:
    pass


class QueryFeature(ABC):
    """
    Base class for all domain-level query features.
    """

    @abstractmethod
    def apply(self, query: Select | None, context: dict) -> Select:
        """
        query   -> current SQLAlchemy Select (or None if first feature)
        context -> shared state between features (model, params, joins later, etc.)
        """
        pass
