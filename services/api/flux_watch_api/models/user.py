from dataclasses import dataclass

from flux_watch_api.models.auth import Scheme


@dataclass
class AuthUser:
    auth_scheme: Scheme
    credentials: str
    principal: str
