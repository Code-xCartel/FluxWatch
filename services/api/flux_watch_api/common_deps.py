from flux_watch_api.core.app import App
from flux_watch_api.core.registry import registry
from flux_watch_api.database.redis import Redis
from flux_watch_api.database.session import Database, DatabaseConnectionConfig


def register_common_deps(app: App) -> None:
    registry.register(Database, url=app.config.PG_URL, config=DatabaseConnectionConfig.API)
    registry.register(Redis, redis_url=app.config.REDIS_URL)
