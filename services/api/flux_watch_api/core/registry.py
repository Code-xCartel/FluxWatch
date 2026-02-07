from collections.abc import Callable
from typing import Any

from flux_watch_api.core.class_helper import Singleton


class AppRegistry(metaclass=Singleton):
    def __init__(self):
        self._dependencies: dict[Callable, Any] = {}

    def register(self, dependency: Callable, **kwargs):
        self._dependencies[dependency] = dependency(**kwargs)

    def resolve(self, dependency: Callable):
        if dependency not in self._dependencies:
            self.register(dependency)
        return self._dependencies[dependency]


registry = AppRegistry()
