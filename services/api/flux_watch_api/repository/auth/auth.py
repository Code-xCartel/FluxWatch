from fastapi import Depends

from flux_watch_api.core.base_repository import Repository
from flux_watch_api.database.query_builder.base import QueryModel
from flux_watch_api.database.query_builder.features import FilterFeature, ModelFeature
from flux_watch_api.errors.rest_errors import UnauthorizedError
from flux_watch_api.models.account import AccountCreate, AccountLogin
from flux_watch_api.schema import AccountCredsORM, AccountORM
from flux_watch_api.utils.auth_utils import AuthUtils


class AccountSearch(QueryModel):
    features = [
        ModelFeature(AccountORM),
        FilterFeature("principal", "email"),
    ]


class AuthRepository:
    def __init__(self, repo: Repository = Depends(), auth_utils: AuthUtils = Depends()):
        self.repo = repo
        self.auth_utils = auth_utils

    def create_account(self, account_details: AccountCreate) -> None:
        hashed_pass = self.auth_utils.hash_password(account_details.password)

        _account = AccountORM(
            name=account_details.name,
            principal=account_details.email,
            is_active=False,
            is_locked=False,
            credentials=AccountCredsORM(
                password_hash=hashed_pass,
            ),
        )

        self.repo.add_one(_account)
        return

    def authenticate_account(self, account_details: AccountLogin):
        account: AccountORM = self.repo.get_one(AccountSearch, account_details.to_dict())
        if not self.auth_utils.validate_password(
            account_details.password, account.credentials.password_hash
        ):
            raise UnauthorizedError

        session = self.repo.add_one(self.auth_utils.make_session(account=account))

        return session
