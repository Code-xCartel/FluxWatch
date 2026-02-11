from typing import Generic, TypeVar

from flux_watch_api.models.base import APIModel

T = TypeVar("T")


class Meta(APIModel):
    returned_count: int
    total_count: int


class ListResponse(APIModel, Generic[T]):
    meta: Meta
    results: list[T]
