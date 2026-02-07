from services.api.flux_watch_api.core.config import AppConfig
from services.api.flux_watch_api.database.session import get_session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, app_config: AppConfig):
        super().__init__(app)
        self.app_config = app_config

    @staticmethod
    def authenticate_user(token, db):
        return {
            "token": token,
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        session_gen = get_session()
        db = next(session_gen)  # open session

        try:
            token = request.headers.get("Authorization")

            user = None
            if token:
                user = self.authenticate_user(token, db)

            request.state.user = user

            response = await call_next(request)
            return response

        finally:
            try:
                next(session_gen)  # close session
            except StopIteration:
                pass
