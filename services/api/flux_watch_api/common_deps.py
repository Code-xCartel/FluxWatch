import logging
import logging.config

from flux_watch_api.core.config import AppConfig
from flux_watch_api.core.registry import registry
from flux_watch_api.database.redis import Redis
from flux_watch_api.database.session import Database, DatabaseConnectionConfig


def register_common_deps(init_logger: bool = True) -> None:
    registry.register(AppConfig)
    _config = registry.resolve(AppConfig)

    if init_logger:
        logging.config.dictConfig(_config.LOGGING_CONFIG)

    registry.register(Database, url=_config.PG_URL, config=DatabaseConnectionConfig.API)
    registry.register(Redis, redis_url=_config.REDIS_URL)
