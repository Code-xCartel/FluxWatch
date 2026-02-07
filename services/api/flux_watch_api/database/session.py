import logging
from collections.abc import Generator
from enum import Enum
from typing import Any

from services.api.flux_watch_api.core.config import get_env
from sqlalchemy import create_engine, orm

logger = logging.getLogger(__name__)


class DatabaseConnectionConfig(Enum):
    API = {
        "pool_size": 10,
        "max_overflow": 15,
        "pool_timeout": 60,
        "pool_recycle": 3600,
    }


_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(get_env("PG_URL"), **DatabaseConnectionConfig.API.value)
        logger.info("Initialized Postgres Engine.")
    return _engine


SessionLocal = orm.sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_session() -> Generator[orm.Session, Any, None]:
    session = SessionLocal(bind=_get_engine())
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
