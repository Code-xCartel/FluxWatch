import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends

from flux_watch_api.core.base_repository import Repository
from flux_watch_api.models.common import AccountSearch
from flux_watch_api.schema import AccountApiKeyORM, AccountORM
from flux_watch_api.utils.auth import AuthUtils


class ApiKeysRepository:
    def __init__(self, repo: Repository = Depends(), auth_utils: AuthUtils = Depends()):
        self.repo = repo
        self.auth_utils = auth_utils

    @staticmethod
    def _generate_api_key(length: int = 32) -> str:
        return secrets.token_urlsafe(length)

    @property
    def daily_limit(self):
        return self.repo.app_config.API_KEY_DAILY_LIMIT

    def get_key(self):
        acc: AccountORM = self.repo.get_one(AccountSearch, principal=self.repo.principal)
        return acc.api_key

    def generate_new_key(self):
        acc: AccountORM = self.repo.get_one(AccountSearch, principal=self.repo.principal)

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=self.repo.app_config.API_KEY_TTL_DAYS)
        key_value = self._generate_api_key()
        hashed_key = self.auth_utils.hash_password(key_value)

        if acc.api_key:
            acc.api_key.api_key = hashed_key
            acc.api_key.ttl = expires_at
            acc.api_key.is_active = True
            acc.api_key.usage_count = 0
            acc.api_key.last_used_at = None
            acc.api_key.usage_window_start = None
            acc.api_key.daily_limit = self.daily_limit
        else:
            api_key_record = AccountApiKeyORM(
                account=acc,
                api_key=hashed_key,
                ttl=expires_at,
                is_active=True,
                usage_count=0,
                daily_limit=self.daily_limit,
            )
            self.repo.add_one(api_key_record)

        return key_value
