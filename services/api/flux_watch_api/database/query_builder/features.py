from sqlalchemy import or_, select

from flux_watch_api.database.query_builder.base import QueryFeature


class ModelFeature(QueryFeature):
    """
    Initializes the query with the ORM model.
    """

    def __init__(self, model):
        self.model = model

    def apply(self, query, context):
        context["model"] = self.model
        return select(self.model)


class FilterFeature(QueryFeature):
    """
    Handles filters, the field and operator separated by __
    """

    OPERATORS = {
        "eq": lambda c, v: c == v,
        "ne": lambda c, v: c != v,
        "gt": lambda c, v: c > v,
        "gte": lambda c, v: c >= v,
        "lt": lambda c, v: c < v,
        "lte": lambda c, v: c <= v,
        "ilike": lambda c, v: c.ilike(f"%{v}%"),
        "like": lambda c, v: c.like(f"%{v}%"),
        "in": lambda c, v: c.in_(v.split(",")),
    }

    def __init__(self, field: str, param_prefix: str | None = None):
        self.field = field
        self.param_prefix = param_prefix or field

    def apply(self, query, context):
        model = context["model"]
        params = context["params"]

        column = getattr(model, self.field, None)
        if column is None:
            return query

        for key, value in params.items():
            if not key.startswith(self.param_prefix):
                continue

            parts = key.split("__")
            op = parts[1] if len(parts) > 1 else "eq"

            operator = self.OPERATORS.get(op)
            if operator:
                query = query.where(operator(column, value))

        return query


class SearchFeature(QueryFeature):
    """
    Handles:
    ?search=harsh
    across multiple fields
    """

    def __init__(self, param_name: str, fields: list[str]):
        self.param_name = param_name
        self.fields = fields

    def apply(self, query, context):
        model = context["model"]
        params = context["params"]

        value = params.get(self.param_name)
        if not value:
            return query

        conditions = [
            getattr(model, f).ilike(f"%{value}%") for f in self.fields if hasattr(model, f)
        ]

        return query.where(or_(*conditions)) if conditions else query
