import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from flux_watch_api.core.registry import registry
from flux_watch_api.database.redis import Redis
from flux_watch_api.database.session import Database

logger = logging.getLogger(__name__)

health_check_router = APIRouter()


@health_check_router.get("/health")
def health_check():
    checks: dict[str, str] = {}

    try:
        db: Database = registry.resolve(Database)
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        logger.exception("Health check: database probe failed")
        checks["database"] = "unavailable"

    try:
        redis: Redis = registry.resolve(Redis)
        redis.client.ping()
        checks["redis"] = "ok"
    except Exception:
        logger.exception("Health check: redis probe failed")
        checks["redis"] = "unavailable"

    all_ok = all(v == "ok" for v in checks.values())
    return JSONResponse(
        status_code=200 if all_ok else 503,
        content={"status": "ok" if all_ok else "degraded", "checks": checks},
    )
