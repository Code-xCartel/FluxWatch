import logging
from contextlib import asynccontextmanager

from fastapi import Depends, Request
from starlette.middleware.cors import CORSMiddleware

from flux_watch_api.common_deps import register_common_deps
from flux_watch_api.core.app import App
from flux_watch_api.core.config import AppConfig
from flux_watch_api.core.registry import registry
from flux_watch_api.database.redis import Redis
from flux_watch_api.errors.rest_errors import ServerError
from flux_watch_api.middlewares.auth import auth_middleware
from flux_watch_api.routes.routes import router
from flux_watch_api.utils.cors import ALLOWED_HEADERS, ALLOWED_METHODS

logger = logging.getLogger(__name__)


def create_app() -> App:
    register_common_deps()
    _config: AppConfig = registry.resolve(AppConfig)

    @asynccontextmanager
    async def lifespan(_app: App):
        yield
        registry.resolve(Redis).flush()

    _app = App(
        title="FluxWatch API Service",
        version="1.0",
        description="Easy stream service for fluxWatch analytics",
        openapi_url=f"{_config.API_PREFIX}/openapi.json",
        docs_url=f"{_config.API_PREFIX}/docs",
        redoc_url=f"{_config.API_PREFIX}/redoc",
        config=_config,
        lifespan=lifespan,
    )

    @_app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception on %s %s", request.method, request.url.path, exc_info=exc)
        return ServerError

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=_config.ALLOWED_ORIGINS,
        allow_methods=ALLOWED_METHODS,
        allow_headers=ALLOWED_HEADERS,
        allow_credentials=True,
    )
    _app.include_router(
        router=router, prefix=_app.config.API_PREFIX, dependencies=[Depends(auth_middleware)]
    )

    return _app
