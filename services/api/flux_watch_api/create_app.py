import logging.config

from fastapi import Depends
from starlette.middleware.cors import CORSMiddleware

from flux_watch_api.common_deps import register_common_deps
from flux_watch_api.core.app import App
from flux_watch_api.core.config import AppConfig
from flux_watch_api.core.registry import registry
from flux_watch_api.middlewares.auth import auth_middleware
from flux_watch_api.routes.routes import router


def create_app() -> App:
    _config: AppConfig = registry.resolve(AppConfig)

    _app = App(
        title="FluxWatch API Service",
        version="1.0",
        description="Easy stream service for fluxWatch analytics",
        openapi_url=f"{_config.API_PREFIX}/openapi.json",
        docs_url=f"{_config.API_PREFIX}/docs",
        redoc_url=f"{_config.API_PREFIX}/redoc",
        config=_config,
    )

    logging.config.dictConfig(_app.config.LOGGING_CONFIG)
    register_common_deps(app=_app)

    _app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )
    _app.include_router(
        router=router, prefix=_app.config.API_PREFIX, dependencies=[Depends(auth_middleware)]
    )

    return _app
