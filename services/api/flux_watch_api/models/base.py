from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class APIModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # allow snake_case input too
        extra="forbid",  # ideal, but can be overridden in child class
        from_attributes=True,
    )

    __model__ = None

    def get_orm(self) -> type:
        if not self.__model__:
            raise AttributeError("API model has not been initialized with an orm config")
        return self.__model__

    def to_dict(self):
        d = {}
        for k, v in self.__dict__.items():
            d[k] = v
        return d


class ResourceModel(APIModel):
    """Mixin that adds standard resource fields (id, created_at, updated_at) to response models."""

    id: UUID
    created_at: datetime
    updated_at: datetime
