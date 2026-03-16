from flux_watch_api.database.query_builder.base import QueryModel
from flux_watch_api.database.query_builder.features import FilterFeature, ModelFeature
from flux_watch_api.schema import AccountORM


class AccountSearch(QueryModel):
    features = [
        ModelFeature(AccountORM),
        FilterFeature("principal"),
    ]
