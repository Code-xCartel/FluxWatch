from fastapi import FastAPI
from services.api.flux_watch_api.api.routes import router


def create_app() -> FastAPI:
    _app = FastAPI(
        title="FluxWatch API Service",
        version="1.0",
        description="Easy stream service for fluxWatch analytics",
    )

    _app.include_router(router=router)

    return _app
