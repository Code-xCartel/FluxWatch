from flux_watch_api.core.base_repository import Repository
from flux_watch_api.errors.rest_errors import UnauthorizedError
from flux_watch_api.managers.auth.plugins.abstract import Plugin
from flux_watch_api.models.auth import Scheme
from flux_watch_api.models.common import AccountSearch
from flux_watch_api.models.user import AuthUser
from flux_watch_api.schema import AccountORM, AccountSessionORM
from flux_watch_api.utils.auth import AuthUtils
from flux_watch_api.utils.utilities import extract_auth_user


class ResidentPlugin(Plugin):
    def __init__(self, repo: Repository, auth_utils: AuthUtils):
        super().__init__()
        self._handler = repo
        self._auth_utils = auth_utils

    def authenticate(self, auth_user: AuthUser, **kwargs) -> AccountSessionORM:
        account: AccountORM = self._handler.get_one(
            AccountSearch, {"principal": auth_user.principal}
        )

        if not account.is_active and not kwargs.get("skip_active_check", False):
            raise UnauthorizedError(detail="Account is not active")

        if account.is_locked:
            raise UnauthorizedError(detail="Account is locked")

        if not self._auth_utils.validate_password(
            auth_user.credentials, account.credentials.password_hash
        ):
            raise UnauthorizedError(detail="Invalid credentials")

        return self._auth_utils.make_session(account=account)

    def extract(self, cred: str) -> AuthUser:
        return extract_auth_user(scheme=Scheme.RESIDENT, encoded=cred)
