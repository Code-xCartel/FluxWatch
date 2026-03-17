from typing import Any

from fastapi import Depends
from starlette.requests import Request

from flux_watch_api.core.config import AppConfig
from flux_watch_api.core.registry import registry
from flux_watch_api.database.client import SQLClient
from flux_watch_api.models.account import AccountSession


class Repository:
    def __init__(self, request: Request, client: SQLClient = Depends()):
        self._client = client
        self._request = request
        self.app_config: AppConfig = registry.resolve(AppConfig)

    @property
    def session(self) -> AccountSession | None:
        return getattr(self._request.state, "session", None)

    def add_one(self, obj: Any):
        return self._client.add_one(obj)

    def get_one(self, *args, **kwargs):
        return self._client.get_one(*args, **kwargs)

    def get_many(self, *args, **kwargs):
        return self._client.get_many(*args, **kwargs)

    def delete_one(self, *args, **kwargs):
        return self._client.delete_one(*args, **kwargs)
