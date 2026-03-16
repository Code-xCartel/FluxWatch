import base64

from flux_watch_api.errors.rest_errors import UnauthorizedError
from flux_watch_api.models.auth import Scheme
from flux_watch_api.models.user import AuthUser


def extract_auth_user(scheme: Scheme, encoded: str) -> AuthUser:
    try:
        creds, principal = base64.b64decode(encoded).decode().split(":", 1)
        return AuthUser(auth_scheme=scheme, credentials=creds, principal=principal)
    except (UnicodeDecodeError, ValueError) as e:
        raise UnauthorizedError(detail="Invalid token") from e
