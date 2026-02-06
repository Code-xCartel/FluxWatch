import logging
import os
from collections.abc import Generator
from enum import Enum
from typing import Any

from sqlalchemy import create_engine, orm

logger = logging.getLogger(__name__)


class DatabaseConnectionConfig(Enum):
    API = {
        "pool_size": 10,
        "max_overflow": 15,
        "pool_timeout": 60,
        "pool_recycle": 3600,
    }


engine = create_engine(os.environ["PG_URL"], **DatabaseConnectionConfig.API.value)
logger.info("Initialized Postgres Engine.")

SessionLocal = orm.sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_session() -> Generator[orm.Session, Any, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
