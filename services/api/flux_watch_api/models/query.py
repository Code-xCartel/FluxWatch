from fastapi import Query as Q
from pydantic import BaseModel


class Query(BaseModel):
    page_size: int | None = Q(alias="pageSize", default=10)
    page: int | None = Q(default=1)
    search: str | None = Q(default=None)
    order: str | None = Q(default=None)

    def as_dict(self):
        return {
            "page_size": self.page_size,
            "page": self.page,
            "search": self.search,
            "order": self.order,
        }
