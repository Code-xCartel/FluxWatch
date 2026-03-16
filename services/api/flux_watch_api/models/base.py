from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class APIModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # allow snake_case input too
        extra="forbid",  # ideal, but can be overridden in child class
    )

    def get_orm(self):
        return f"{self.__name__}ORM"

    def to_dict(self):
        d = {}
        for k, v in self.__dict__.items():
            d[k] = v
        return d
