import abc

from flux_watch_api.models.user import AuthUser
from flux_watch_api.schema import AccountSessionORM


class Plugin(abc.ABC):
    @abc.abstractmethod
    def authenticate(self, auth_user: AuthUser) -> AccountSessionORM:
        raise NotImplementedError

    @abc.abstractmethod
    def extract(self, cred: str) -> AuthUser:
        raise NotImplementedError
