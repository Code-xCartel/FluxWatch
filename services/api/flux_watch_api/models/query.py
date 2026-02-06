from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel


class _Query(BaseModel):
    query: str | None = None
    limit: int | None = 50
    offset: int | None = 0
    search: str | None = None


Query = Annotated[_Query, Depends()]
