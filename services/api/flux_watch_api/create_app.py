from services.api.flux_watch_api.api.routes import router
from services.api.flux_watch_api.core.app import App
from services.api.flux_watch_api.core.config import AppConfig
from services.api.flux_watch_api.core.registry import registry
from starlette.middleware.cors import CORSMiddleware

# from services.api.flux_watch_api.middlewares.auth import AuthMiddleware


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

    _app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )
    # _app.add_middleware(AuthMiddleware, app=_app, app_config=_config)
    _app.include_router(router=router, prefix=_config.API_PREFIX)

    return _app
