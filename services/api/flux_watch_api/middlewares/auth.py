from fastapi import Depends
from starlette.requests import Request

from flux_watch_api.core.config import AppConfig
from flux_watch_api.errors.rest_errors import UnauthorizedError
from flux_watch_api.managers.auth.auth_manager import AuthManager


def auth_middleware(
    request: Request, auth_manager: AuthManager = Depends(), app_config: AppConfig = Depends()
):
    for path_regex in app_config.skip_auth_routes:
        if path_regex.match(request.url.path):
            return

    session = auth_manager.authenticate(auth_header=request.headers.get("Authorization", None))
    if session is None:
        raise UnauthorizedError

    request.state.session = session.account
    return
