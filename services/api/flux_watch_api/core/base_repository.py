from typing import Any

from fastapi import Depends
from services.api.flux_watch_api.core.config import AppConfig
from services.api.flux_watch_api.core.registry import registry
from services.api.flux_watch_api.database.client import SQLClient
from starlette.requests import Request


def get_user(request: Request) -> dict:
    # return request.state.get("client")
    return {
        "request": request,
    }


class Repository:
    def __init__(self, user: dict = Depends(get_user), client: SQLClient = Depends()):
        self._client = client
        self.user = user
        self.app_config: AppConfig = registry.resolve(AppConfig)

    def add_one(self, obj: Any):
        return self._client.add_one(obj)

    def get_one(self, *args, **kwargs):
        return self._client.get_one(*args, **kwargs)
