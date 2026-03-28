from fastapi.params import Depends

from flux_watch_api.core.base_repository import Repository
from flux_watch_api.errors.rest_errors import UnauthorizedError
from flux_watch_api.managers.auth.plugins.abstract import Plugin
from flux_watch_api.managers.auth.plugins.builder import build_plugins
from flux_watch_api.models.account import AccountSession, Sessions
from flux_watch_api.models.auth import LogoutScope
from flux_watch_api.models.common import AccountSearch
from flux_watch_api.models.user import AuthUser
from flux_watch_api.schema import AccountCredsORM, AccountORM, AccountSessionORM
from flux_watch_api.utils.auth import AuthUtils


class AuthManager:
    def __init__(self, repo: Repository = Depends(), auth_utils: AuthUtils = Depends()):
        self.repo = repo
        self.auth_utils = auth_utils
        self._plugins = build_plugins(repo=repo, auth_utils=auth_utils)

    def _build_auth_user(self, auth_header: str) -> tuple[AuthUser, Plugin]:
        if not auth_header:
            raise UnauthorizedError("No auth header provided")

        auth_header = auth_header.strip()

        try:
            scheme, creds = auth_header.split(" ", 1)
        except ValueError as e:
            raise UnauthorizedError(detail="Invalid auth header") from e

        plugin = self._plugins.get(scheme)

        if not plugin:
            raise UnauthorizedError(detail="Invalid auth scheme")

        auth_user = plugin.extract(cred=creds)
        return auth_user, plugin

    def _authenticate(self, auth_header: str, skip_active_check=False) -> AccountSessionORM:
        auth_user, plugin = self._build_auth_user(auth_header=auth_header)
        return plugin.authenticate(auth_user=auth_user, skip_active_check=skip_active_check)

    def authenticate(self, auth_header: str) -> AccountSession:
        _session = self._authenticate(auth_header=auth_header)
        return self.auth_utils.enrich_session(session=_session)

    def authenticate_and_save(self, auth_header: str) -> AccountSession:
        _session = self._authenticate(auth_header=auth_header, skip_active_check=True)
        session = self.repo.add_one(_session)
        return self.auth_utils.enrich_session(session=session)

    def create_new(self, name: str, email: str, password: str) -> str:
        hashed_pass = self.auth_utils.hash_password(password)

        _account = AccountORM(
            name=name,
            principal=email,
            is_active=False,
            is_locked=False,
            credentials=AccountCredsORM(
                password_hash=hashed_pass,
            ),
        )
        self.repo.add_one(_account)

        # create temporary session
        temp_session = self.auth_utils.make_session(account=_account, ttl_days=0.1)
        s = self.repo.add_one(temp_session)
        return self.auth_utils.enrich_session(session=s).access_token

    def activate_account(self, auth_header: str):
        session = self._authenticate(auth_header=auth_header, skip_active_check=True)
        session.account.is_active = True
        return self.repo.add_one(session.account)

    def delete_sessions(self, auth_header: str, scope: LogoutScope):
        session = self._authenticate(auth_header=auth_header)
        if scope == LogoutScope.CURRENT:
            return self.repo.delete_one(session)
        else:
            all_session = [
                s for s in session.account.sessions if not s.expired
            ]  # back population??
            for session in all_session:
                self.repo.delete_one(session)
            return None

    def new_temp_session(self, auth_header: str) -> AccountSession:
        auth_user, _ = self._build_auth_user(auth_header=auth_header)
        account: AccountORM = self.repo.get_one(AccountSearch, {"principal": auth_user.principal})

        if len(account.sessions) > 1:
            raise UnauthorizedError(detail="Account already has more than one sessions")

        self.repo.delete_one(account.sessions[0])
        temp_session = self.auth_utils.make_session(account=account, ttl_days=0.1)
        s = self.repo.add_one(temp_session)
        return self.auth_utils.enrich_session(session=s)

    def get_sessions(self, auth_header: str):
        auth_user, _ = self._build_auth_user(auth_header=auth_header)
        account: AccountORM = self.repo.get_one(AccountSearch, {"principal": auth_user.principal})

        active_sessions = [
            Sessions.model_validate(s)
            for s in account.sessions
            if not s.expired and not str(s.id) == auth_user.credentials
        ]

        return active_sessions
