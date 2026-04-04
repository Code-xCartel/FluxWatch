import logging
from collections.abc import Generator
from enum import Enum

from fastapi import Depends
from sqlalchemy import create_engine, orm

from flux_watch_api.core.registry import registry

logger = logging.getLogger(__name__)


class DatabaseConnectionConfig(Enum):
    API = {
        "pool_size": 10,
        "max_overflow": 15,
        "pool_timeout": 60,
        "pool_recycle": 3600,
    }


class Database:
    def __init__(self, url: str, config: DatabaseConnectionConfig):
        logger.info("Initializing Postgres Engine.")
        try:
            self.engine = create_engine(url, **config.value)
            logger.info("Initialized Postgres Engine.")
        except Exception as e:
            logger.error("Failed to initialize Postgres Engine: " + str(e))

        self.session_local = orm.sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine, expire_on_commit=False
        )

    def get_session(self) -> Generator[orm.Session, None, None]:
        session = self.session_local()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


# hack
def InjectSession():
    def _session():
        db = registry.resolve(Database)
        yield from db.get_session()

    return Depends(_session)
