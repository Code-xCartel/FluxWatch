from sqlalchemy import func, select

from flux_watch_api.database.query_builder.processor import Pagination, Sorting


class QueryBuilder:
    """
    Executes feature pipeline + applies result shaping (sorting & pagination)
    """

    def __init__(self, schema_cls, params: dict):
        self.schema = schema_cls
        self.params = params
        self.context = {"params": params}

        self.sorting = Sorting()
        self.pagination = Pagination()

    def _build_base(self):
        query = None
        for feature in self.schema.features:
            query = feature.apply(query, self.context)
        return query

    def build(self, paginate: bool = True, sort: bool = True, with_counts: bool = False):
        base_query = self._build_base()
        model = self.context["model"]

        data_query = base_query

        if sort:
            data_query = self.sorting.apply(
                query=data_query,
                model=model,
                params=self.params,
                default_ordering=getattr(self.schema, "default_ordering", None),
            )

        if paginate:
            data_query = self.pagination.apply(
                query=data_query,
                params=self.params,
                max_page_size=getattr(self.schema, "max_page_size", None),
            )

        count_query = None
        if with_counts:
            count_query = select(func.count()).select_from(base_query.subquery())

        return data_query, count_query
